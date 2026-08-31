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

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from gcp_router import decisions as dec
from gcp_router import delegation as dlg
from gcp_router.demo_page import PAGE as DEMO_PAGE

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOUR = ROOT / "local_tour"
REGISTRY_PATH = TOUR / "registry.json"
FLEET_PATH = TOUR / "fleet.json"
PLATFORM_PATH = TOUR / "platform.json"

# Candidate models, tried in order; the first one the key accepts is kept.
MODEL_CANDIDATES = [
    m.strip() for m in os.environ.get(
        "GEMINI_MODELS",
        "gemini-3.5-flash,gemini-flash-latest,gemini-2.5-flash,gemini-2.0-flash",
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


_MAP_CACHE = {}


def carte_answer(argv):
    """read_carte served in-process: the map is parsed once, then reused.

    Spawning a fresh interpreter and re-reading a 104 KB file on every request
    was costing ~1 s each under batch load. The circuit script stays the
    reference implementation; this is the same logic without the fork.
    """
    import importlib.util
    if "mod" not in _MAP_CACHE:
        spec = importlib.util.spec_from_file_location(
            "carte_circuit", TOUR / "circuits" / "relever-carte-apps.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MAP_CACHE["mod"] = mod
        _MAP_CACHE["data"], _MAP_CACHE["zones"] = mod.load()
    mod, data, zones = _MAP_CACHE["mod"], _MAP_CACHE["data"], _MAP_CACHE["zones"]
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if not argv:
            mod.summary(data, zones)
        elif argv[0] == "--zone" and len(argv) > 1:
            mod.one_zone(zones, " ".join(argv[1:]))
        else:
            mod.search(zones, argv)
    return buf.getvalue().strip()


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
        if call.name == "read_carte":
            output = carte_answer(list(call.args.get("argv", [])))
        else:
            proc = subprocess.run(["python3", str(script)], capture_output=True,
                                  text=True, cwd=str(TOUR), timeout=60)
            output = proc.stdout.strip()
        STATS["deterministic"] += 1
        record = {"capability": call.name, "decision": "MATCH",
                  "llm_required": False, "route": "deterministic",
                  "matched": entry["path"], "result": output,
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


# --- asynchronous batch work -------------------------------------------------
JOBS = {}


class Batch(BaseModel):
    requests: list = []
    label: str = "batch"


def _route_one(name, args):
    """The same routing decision as /mcp/tour, without the HTTP layer."""
    started = time.time()
    registry = load_registry()
    entry = registry.get(name)
    allowed, reason = guardrail_verdict(name, entry, args)
    if not allowed:
        return {"capability": name, "decision": "REFUSED", "reason": reason,
                "model_calls": 0, "ms": round((time.time() - started) * 1000)}
    if entry:
        script = TOUR / entry["path"]
        if not script.exists():
            return {"capability": name, "decision": "ERROR",
                    "reason": "circuit missing", "model_calls": 0,
                    "ms": round((time.time() - started) * 1000)}
        if name == "read_carte":
            out = carte_answer(list(args.get("argv", [])))
        else:
            proc = subprocess.run(["python3", str(script)] + list(args.get("argv", [])),
                                  capture_output=True, text=True, cwd=str(TOUR),
                                  timeout=60)
            out = proc.stdout.strip()
        return {"capability": name, "decision": "MATCH",
                "result": out[:400], "model_calls": 0,
                "ms": round((time.time() - started) * 1000)}
    known = ", ".join(registry.keys()) or "(none)"
    prompt = ("Fallback reasoner of a deterministic control plane. Known: %s. "
              "Unknown capability '%s' with args %s. In one sentence, say what "
              "a new circuit would have to do." % (known, name, json.dumps(args)))
    try:
        model, text = gemini_answer(prompt)
    except Exception as exc:
        return {"capability": name, "decision": "ERROR", "reason": str(exc)[:120],
                "model_calls": 0, "ms": round((time.time() - started) * 1000)}
    return {"capability": name, "decision": "NO_MATCH", "model": model,
            "result": text[:400], "model_calls": 1,
            "ms": round((time.time() - started) * 1000)}


def _run_batch(job_id, items):
    job = JOBS[job_id]
    for i, it in enumerate(items):
        rec = _route_one(it.get("name", ""), it.get("args", {}) or {})
        job["results"].append(rec)
        job["done"] = i + 1
        job["model_calls"] += rec.get("model_calls", 0)
        if rec["decision"] == "MATCH":
            job["deterministic"] += 1
        elif rec["decision"] == "NO_MATCH":
            job["llm"] += 1
        elif rec["decision"] == "REFUSED":
            job["refused"] += 1
        else:
            job["errors"] += 1
    job["state"] = "finished"
    job["finished_ms"] = round((time.time() - job["_t0"]) * 1000)


@app.post("/batch")
async def submit_batch(batch: Batch, background: BackgroundTasks):
    """Hand over a pile of work and walk away. Returns a job id immediately."""
    if not batch.requests:
        raise HTTPException(status_code=400, detail="requests is empty")
    if len(batch.requests) > 5000:
        raise HTTPException(status_code=400, detail="at most 5000 per batch")
    job_id = "job-%d-%d" % (len(JOBS) + 1, int(time.time() * 1000) % 100000)
    JOBS[job_id] = {"id": job_id, "label": batch.label, "state": "running",
                    "total": len(batch.requests), "done": 0,
                    "deterministic": 0, "llm": 0, "refused": 0, "errors": 0,
                    "model_calls": 0, "results": [], "_t0": time.time()}
    background.add_task(_run_batch, job_id, list(batch.requests))
    return {"job_id": job_id, "state": "running", "total": len(batch.requests),
            "poll": "/batch/" + job_id}


@app.get("/batch/{job_id}")
async def batch_status(job_id: str, full: bool = False):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="no such job")
    out = {k: v for k, v in job.items() if not k.startswith("_") and k != "results"}
    total_answered = job["deterministic"] + job["llm"] + job["refused"]
    if total_answered:
        out["share_without_model"] = round(
            100.0 * (job["deterministic"] + job["refused"]) / total_answered, 1)
    out["results"] = job["results"] if full else job["results"][-5:]
    return out


@app.get("/batch")
async def batch_list():
    return {"jobs": [{k: v for k, v in j.items()
                      if k in ("id", "label", "state", "total", "done",
                               "deterministic", "llm", "model_calls")}
                     for j in JOBS.values()]}


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


def load_fleet():
    with open(FLEET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class Mission(BaseModel):
    request: str


@app.post("/delegate")
async def delegate(m: Mission):
    """Split one request across the specialised sub-agents that can take it.

    This is what the category asks for: not one agent with many prompts, but a
    fleet where each member has a written specification, and where the routing
    refuses to hand an agent work its own specification forbids.
    """
    if not m.request.strip():
        raise HTTPException(status_code=400, detail="request is empty")
    try:
        return dlg.delegate(m.request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/fleet")
async def fleet():
    """The agents this control plane governs, and what each is allowed to do.

    A fleet is not one agent with many prompts. These are distinct agents with
    written specifications, each bound to an engine -- including agents bound to
    no model at all ("lecture-seule": deterministic code only). Any engine can
    execute any specification, which is why the control plane, and not the
    model, is what makes behaviour predictable.
    """
    agents = load_fleet()
    engines = {}
    for a in agents:
        engines[a["engine"]] = engines.get(a["engine"], 0) + 1
    no_model = sum(1 for a in agents if a["engine"] in ("lecture-seule", "none"))
    return {
        "agents": len(agents),
        "engines": engines,
        "agents_running_without_any_model": no_model,
        "specification_chars_total": sum(a["spec_chars"] for a in agents),
        "permissions": {
            "may_publish": sum(1 for a in agents if a["may_publish"]),
            "may_decide": sum(1 for a in agents if a["may_decide"]),
            "may_modify": sum(1 for a in agents if a["may_modify"]),
        },
        "note": ("Engines are interchangeable: a specification written for one "
                 "agent can be executed by Gemini, by a local model, or by no "
                 "model at all. The guardrails and circuits do not change."),
        "fleet": agents,
    }


@app.get("/platform")
async def platform():
    """What already existed before this hackathon, at its real size.

    Disclosing pre-existing work is a rule of the competition. Disclosing it
    honestly means giving its actual scale: a reader told "some experimental
    components" pictures two draft files. These are the production numbers.
    """
    with open(PLATFORM_PATH, "r", encoding="utf-8") as f:
        p = json.load(f)
    return {
        "what_a_director_asks": {
            "control_gates_defined": p["circuit_gates"],
            "gates_actually_passed": p["circuit_steps_passed"],
            "governed_runs": p["circuit_runs"],
            "period": "%s to %s" % (p["oldest_circuit_run"], p["newest_circuit_run"]),
            "meaning": ("Every agent action crossed a gate that could refuse it, "
                        "and every crossing is recorded. That is an audit trail, "
                        "not a log."),
        },
        "platform_scale": {
            "modules_installed": p["modules_installed"],
            "data_models": p["data_models"],
            "memory_rows": p["memory_rows"],
            "circuit_templates": p["circuit_templates"],
            "skills_defined": p["skills_defined"],
            "tools_catalogued": p["tools_catalogued"],
            "backups_taken": p["backups"],
            "agent_events": p["agent_events"],
        },
        "pre_existing": ("The platform above was built before this hackathon and "
                         "runs in production. It is disclosed, at its real size, "
                         "because understating it would be as misleading as "
                         "overstating it."),
        "built_during_the_hackathon": [
            "the deterministic front door (gcp_router/)",
            "the Google GenAI fallback path, on Gemini 3.5 Flash via Vertex AI",
            "the asynchronous batch endpoint",
            "the independent-oracle wiring and /metrics observability",
            "the Cloud Run deployment",
            "the audit script that checks this repository against its own claims",
        ],
        "snapshot_taken": p["snapshot_taken"],
        "source": p["source"],
    }


# --- the decisions desk: a human approves or refuses what an agent proposed ---
class Login(BaseModel):
    login: str
    password: str


class Session(BaseModel):
    uid: int
    cookie: str


class Verdict(BaseModel):
    session: Session
    action: str
    commentaire: str = ""


@app.post("/api/login")
async def decisions_login(body: Login):
    try:
        uid, cookie = dec.authenticate(body.login, body.password)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return {"uid": uid, "cookie": cookie}


@app.post("/api/decisions")
async def decisions_list(body: dict):
    s = (body or {}).get("session") or {}
    if not s.get("uid") or not s.get("cookie"):
        raise HTTPException(status_code=401, detail="Not signed in.")
    try:
        return dec.list_decisions(s["uid"], s["cookie"])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/api/decisions/{decision_id}/action")
async def decisions_act(decision_id: int, body: Verdict):
    try:
        dec.decide(body.session.uid, body.session.cookie, decision_id,
                   body.action, body.commentaire)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"ok": True}


@app.get("/decisions", response_class=HTMLResponse)
async def decisions_page():
    return (pathlib.Path(__file__).parent / "decisions_public" /
            "index.html").read_text(encoding="utf-8")


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


from fastapi.staticfiles import StaticFiles  # noqa: E402

app.mount("/decisions-static",
          StaticFiles(directory=str(pathlib.Path(__file__).parent /
                                    "decisions_public")),
          name="decisions-static")


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
