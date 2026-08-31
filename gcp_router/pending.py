"""Decisions the control plane raises for a human, and the verdicts it records.

When a guardrail refuses an agent, that refusal is not the end of the story: a
person may still want it to happen. So the refusal becomes a decision waiting
for a human, with the reason the machine gave.

Nothing here talks to an external system. The control plane feeds itself from
its own traffic, which is what makes the loop demonstrable end to end:

    an agent asks -> the machine refuses -> a human rules -> it is recorded

A refusal must carry a written reason. A silent "no" teaches nobody anything --
the rule comes from the original decisions desk and is kept deliberately.
"""
import itertools
import time

_ids = itertools.count(1)
DECISIONS = []
MAX = 200


def raise_decision(capability, reason, args, source="guardrail"):
    """Record that the machine refused something, and ask a human about it."""
    d = {
        "id": next(_ids),
        "capability": capability,
        "raised_by": source,
        "machine_verdict": "REFUSED",
        "machine_reason": reason,
        "arguments": args or {},
        "state": "waiting",
        "human_verdict": None,
        "human_reason": None,
        "raised_at_ms": int(time.time() * 1000),
        "ruled_at_ms": None,
    }
    DECISIONS.append(d)
    del DECISIONS[:-MAX]
    return d


def find(decision_id):
    for d in DECISIONS:
        if d["id"] == decision_id:
            return d
    return None


def rule(decision_id, verdict, reason):
    """A human approves or refuses. Refusing requires a written reason."""
    d = find(decision_id)
    if d is None:
        raise KeyError("no such decision")
    if d["state"] != "waiting":
        raise ValueError("this decision was already ruled on")
    if verdict not in ("approve", "refuse"):
        raise ValueError("verdict must be 'approve' or 'refuse'")
    reason = (reason or "").strip()
    if verdict == "refuse" and not reason:
        raise ValueError("Write a reason first: a silent refusal teaches nobody.")
    d["state"] = "approved" if verdict == "approve" else "refused"
    d["human_verdict"] = verdict
    d["human_reason"] = reason
    d["ruled_at_ms"] = int(time.time() * 1000)
    return d


def summary():
    waiting = [d for d in DECISIONS if d["state"] == "waiting"]
    approved = [d for d in DECISIONS if d["state"] == "approved"]
    refused = [d for d in DECISIONS if d["state"] == "refused"]
    ruled = approved + refused
    return {
        "raised": len(DECISIONS),
        "waiting": len(waiting),
        "approved": len(approved),
        "refused_by_human": len(refused),
        "share_overruled": (round(100.0 * len(approved) / len(ruled), 1)
                            if ruled else None),
        "note": ("Every entry began as a machine refusal. A human can overrule "
                 "it, but never silently: refusing requires a written reason."),
    }
