"""Control Tower — deterministic front door in front of the agent fleet.

Thesis (see docs/architecture-diagram.md):

    request -> deterministic router
                 |- known capability -> circuit executed, ZERO model call
                 `- no match         -> Google Gemini decides (fallback)

Every request records which path it took, so the claim "no model call on a
known capability" is measurable at /metrics rather than merely asserted.
"""
import json
import os
import pathlib
import subprocess
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from gcp_router.demo_page import PAGE as DEMO_PAGE

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOUR = ROOT / "local_tour"
REGISTRY_PATH = TOUR / "registry.json"

# Candidate models, tried in order; the first one the key accepts is kept.
MODEL_CANDIDATES = [
    m.strip() for m in os.environ.get(
        "GEMINI_MODELS",
        "gemini-2.5-flash,gemini-flash-latest,gemini-2.0-flash,gemini-1.5-flash",
    ).split(",") if m.strip()
]

# --- guardrails: pure code, no model involved -------------------------------
DENIED = {"drop_database", "delete_all", "shutdown", "rm_rf"}
WRITE_REQUIRES_CONFIRM = True


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def guardrail_verdict(name, entry, args):
    """Same input -> same verdict, always. That is what makes it a control."""
    if name in DENIED:
        return False, "capability '%s' is on the deny list" % name
    if entry and entry.get("permission") == "write" and WRITE_REQUIRES_CONFIRM:
        if not args.get("confirm"):
            return False, "write capability requires args.confirm = true"
    return True, "allowed"


STATS = {"deterministic": 0, "llm": 0, "refused": 0, "model_calls": 0}
TRACE = []

app = FastAPI(title="Control Tower - Fortified Enterprise Fleet")


class ToolCall(BaseModel):
    name: str
    args: dict = {}


_client = None
_model_in_use = None


def _local_answer(prompt):
    """Fallback served by a self-hosted model (Ollama), no Google involved."""
    import urllib.request
    base = os.environ.get("LOCAL_MODEL_URL")
    name = os.environ.get("LOCAL_MODEL_NAME", "qwen2.5:7b")
    payload = json.dumps({"model": name, "prompt": prompt,
                          "stream": False}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/api/generate",
                                 data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return "local/" + name, json.load(r)["response"].strip()


def _clients():
    """Two ways in, tried in order: an API key, then Vertex AI (service identity)."""
    from google import genai
    out = []
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        out.append(("api-key", genai.Client(api_key=key)))
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project:
        loc = os.environ.get("GOOGLE_CLOUD_LOCATION", "europe-west9")
        try:
            out.append(("vertex", genai.Client(vertexai=True, project=project,
                                               location=loc)))
        except Exception:
            pass
    return out


def gemini_answer(prompt):
    """Real call through the Google GenAI SDK. Raises with the true errors."""
    global _client, _model_in_use
    if os.environ.get("FALLBACK") == "local":
        STATS["model_calls"] += 1
        return _local_answer(prompt)
    tried = []
    for how, client in _clients():
        for model in MODEL_CANDIDATES:
            try:
                resp = client.models.generate_content(model=model, contents=prompt)
                _model_in_use = model
                STATS["model_calls"] += 1
                return "%s/%s" % (how, model), (resp.text or "").strip()
            except Exception as exc:
                msg = str(exc)
                tried.append("%s %s -> %s" % (how, model, msg[:180]))
    if not tried:
        raise RuntimeError("no credentials: set GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT")
    raise RuntimeError(" || ".join(tried))


@app.post("/mcp/tour")
async def mcp_router(call: ToolCall):
    started = time.time()
    registry = load_registry()
    entry = registry.get(call.name)

    allowed, reason = guardrail_verdict(call.name, entry, call.args)
    if not allowed:
        STATS["refused"] += 1
        record = {"capability": call.name, "decision": "REFUSED",
                  "llm_required": False, "route": "refused", "reason": reason,
                  "model_calls": 0, "ms": round((time.time() - started) * 1000)}
        TRACE.append(record)
        return {"status": "refused", **record}

    if entry:
        script = TOUR / entry["path"]
        if not script.exists():
            raise HTTPException(status_code=500,
                                detail="circuit file missing: %s" % script)
        proc = subprocess.run(["python3", str(script)], capture_output=True,
                              text=True, cwd=str(TOUR), timeout=60)
        STATS["deterministic"] += 1
        record = {"capability": call.name, "decision": "MATCH",
                  "llm_required": False, "route": "deterministic",
                  "matched": entry["path"], "result": proc.stdout.strip(),
                  "model_calls": 0, "ms": round((time.time() - started) * 1000)}
        TRACE.append(record)
        return {"status": "executed", **record}

    known = ", ".join(registry.keys()) or "(none)"
    prompt = (
        "You are the fallback reasoner of a deterministic agent control plane.\n"
        "Known capabilities: %s.\n"
        "An agent requested the unknown capability '%s' with arguments %s.\n"
        "In at most three sentences, say whether an existing capability covers "
        "it, or what a new circuit would have to do."
    ) % (known, call.name, json.dumps(call.args))
    try:
        model, text = gemini_answer(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502,
                            detail="fallback model unavailable: %s" % exc)
    STATS["llm"] += 1
    record = {"capability": call.name, "decision": "NO_MATCH",
              "llm_required": True, "route": "llm", "model": model,
              "result": text, "model_calls": 1,
              "ms": round((time.time() - started) * 1000)}
    TRACE.append(record)
    return {"status": "reasoned", **record}


@app.post("/verify")
async def verify(payload: dict):
    """Independent oracle: recomputes the expected value with no model at all."""
    oracle = TOUR / "independent_oracle.py"
    value = str(payload.get("input", 5))
    proc = subprocess.run(["python3", str(oracle), value],
                          capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise HTTPException(status_code=400, detail="oracle rejected the input")
    return {"input": int(value), "expected": int(proc.stdout.strip()),
            "model_calls": 0}


@app.get("/metrics")
async def metrics():
    total = STATS["deterministic"] + STATS["llm"] + STATS["refused"]
    return {"requests": total, **STATS, "trace": TRACE[-25:]}


@app.get("/diag")
async def diag():
    """Which credential paths work, and which models answer. No secret leaves."""
    from google import genai
    out = {"has_api_key": bool(os.environ.get("GOOGLE_API_KEY")),
           "project": os.environ.get("GOOGLE_CLOUD_PROJECT"),
           "candidates": MODEL_CANDIDATES, "results": []}
    for how, client in _clients():
        for model in MODEL_CANDIDATES:
            try:
                r = client.models.generate_content(model=model, contents="Say OK.")
                out["results"].append({"via": how, "model": model, "ok": True,
                                       "said": (r.text or "").strip()[:20]})
            except Exception as exc:
                out["results"].append({"via": how, "model": model, "ok": False,
                                       "error": str(exc)[:220]})
    return out


@app.get("/health")
async def health():
    return {"ok": True, "capabilities": sorted(load_registry().keys())}


@app.get("/demo", response_class=HTMLResponse)
async def demo():
    """The clickable demo, served from the same origin as the API."""
    return DEMO_PAGE


@app.get("/", response_class=HTMLResponse)
async def home():
    rows = "".join("<li><code>%s</code></li>" % c
                   for c in sorted(load_registry().keys()))
    return """<!doctype html><meta charset=utf-8>
<title>Control Tower</title>
<style>body{font:16px/1.7 system-ui,sans-serif;max-width:44rem;margin:3rem auto;
padding:0 1rem;color:#111}code{background:#eef;padding:.1rem .35rem;
border-radius:3px}h1{margin-bottom:.2rem}</style>
<h1>Control Tower</h1>
<p><b>Deterministic front door.</b> Known capability &rarr; circuit runs,
<b>zero model calls</b>. No match &rarr; Google Gemini decides.</p>
<h2>Capabilities</h2><ul>%s</ul>
<h2>Endpoints</h2><ul>
<li><code>POST /mcp/tour</code> &mdash; route a capability</li>
<li><code>POST /verify</code> &mdash; independent oracle</li>
<li><code>GET /metrics</code> &mdash; deterministic vs model calls</li>
<li><code>GET /health</code></li></ul>""" % rows
