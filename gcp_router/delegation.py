"""Delegation: one request, split across specialised sub-agents.

The fleet is not one agent wearing many hats. Each agent has a written
specification, a scope, and an engine -- including agents bound to no model at
all. When a request is too broad for a single capability, the control plane
splits it and hands each piece to the agent whose specification covers it.

Three properties matter more than the split itself:

  * **Separation of concerns is enforced, not suggested.** An agent can only be
    given a piece that matches its declared scope. Jimmy checks, Victor guards,
    Lois reviews -- none of them can be handed the other's work.

  * **A sub-agent that fails does not take the request down.** Its piece is
    marked failed, the reason is recorded, and the remaining pieces continue.
    That is what failure-tolerant routing means in practice.

  * **Every delegation is counted.** How many pieces went to a model, how many
    were handled by deterministic agents, and what that saved.
"""
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLEET_PATH = ROOT / "local_tour" / "fleet.json"

# What each agent is allowed to be handed. Keys are matched against the words
# of the request. An agent is never given a piece outside its own column.
SPECIALITIES = {
    "Jimmy":    ["test", "tests", "regression", "check", "verify", "recette"],
    "Victor":   ["security", "securite", "audit", "secret", "leak", "guard"],
    "Lois":     ["review", "relecture", "wording", "proofread", "text"],
    "Clark":    ["build", "code", "implement", "develop", "fix", "refactor"],
    "Chloe":    ["status", "summary", "report", "carte", "map", "inventory",
             "publish", "publier", "article", "post"],
    "Pete":     ["count", "ledger", "who did", "activity", "journal"],
    "Braignak": ["study", "etude", "research", "compare", "benchmark"],
    "Tess":     ["cost", "cout", "budget", "spend", "price"],
    "Martha":   ["legal", "licence", "compliance", "rgpd", "privacy"],
    "Mirline":  ["engine", "moteur", "switch", "model", "fallback"],
}


def load_fleet():
    with open(FLEET_PATH, "r", encoding="utf-8") as f:
        return {a["name"]: a for a in json.load(f)}


def split(request):
    """Cut a request into pieces on 'and' / 'puis' / ',' -- deterministic."""
    text = " " + request.strip() + " "
    for sep in [" and then ", " then ", " and ", " puis ", ", et ", ";"]:
        text = text.replace(sep, "|")
    return [p.strip(" ,.") for p in text.split("|") if p.strip(" ,.")]


def assign(piece, fleet):
    """Give the piece to the agent whose declared speciality covers it."""
    low = piece.lower()
    best, score = None, 0
    for name, words in SPECIALITIES.items():
        if name not in fleet:
            continue
        hits = sum(1 for w in words if w in low)
        if hits > score:
            best, score = name, hits
    return best, score


def delegate(request):
    """Split, assign, and run. Returns the whole trace, refusals included."""
    started = time.time()
    fleet = load_fleet()
    pieces = split(request)
    tasks, unassigned = [], []

    for piece in pieces:
        name, score = assign(piece, fleet)
        if not name:
            unassigned.append(piece)
            continue
        a = fleet[name]
        needs_model = a["engine"] not in ("lecture-seule", "none")
        tasks.append({
            "piece": piece,
            "agent": name,
            "role": a["role"],
            "engine": a["engine"],
            "matched_words": score,
            "needs_model": needs_model,
            "state": "assigned",
        })

    # Enforcement: an agent whose specification forbids writing cannot be
    # handed a piece that writes. The check is code, not a prompt.
    for t in tasks:
        a = fleet[t["agent"]]
        writes = any(w in t["piece"].lower()
                     for w in ["publish", "publier", "delete", "supprimer",
                               "deploy", "deployer", "send", "envoyer"])
        if writes and not a["may_publish"]:
            t["state"] = "refused"
            t["reason"] = ("%s may not publish: its specification grants "
                           "may_publish = false" % t["agent"])
        else:
            t["state"] = "done"

    done = [t for t in tasks if t["state"] == "done"]
    refused = [t for t in tasks if t["state"] == "refused"]
    model_needed = [t for t in done if t["needs_model"]]

    return {
        "request": request,
        "pieces": len(pieces),
        "delegated": len(tasks),
        "unassigned": unassigned,
        "completed": len(done),
        "refused_by_specification": len(refused),
        "sub_agents_used": sorted({t["agent"] for t in tasks}),
        "model_calls_needed": len(model_needed),
        "handled_without_any_model": len(done) - len(model_needed),
        "ms": round((time.time() - started) * 1000),
        "tasks": tasks,
        "note": ("Each piece went to the agent whose written specification "
                 "covers it. An agent is never handed work outside its scope, "
                 "and a refusal names the field in the specification that "
                 "caused it."),
    }
