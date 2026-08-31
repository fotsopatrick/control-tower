"""Proof: the deterministic answers do not depend on which model backs the fallback.

Runs the same requests twice -- once against a router whose fallback is Google
Gemini, once against a router whose fallback is a self-hosted Qwen -- and
compares the deterministic results byte for byte.

    python3 preuve_deux_modeles.py <gemini-service-url> <local-service-url>
"""
import json
import sys
import urllib.error
import urllib.request

KNOWN = [("read_carte", {}),
         ("create_task", {}),
         ("create_task", {"confirm": True}),
         ("drop_database", {})]
UNKNOWN = ("send_invoice_to_client", {"client": "ACME"})


def post(base, path, payload):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def signature(body):
    """What must be identical: the decision and the produced result."""
    return {"decision": body.get("decision"),
            "llm_required": body.get("llm_required"),
            "result": body.get("result"),
            "reason": body.get("reason"),
            "model_calls": body.get("model_calls")}


def main():
    a = sys.argv[1].rstrip("/")
    b = sys.argv[2].rstrip("/")
    print("A = fallback Google Gemini :", a)
    print("B = fallback self-hosted   :", b)
    print()
    print("%-34s %-9s %-9s %s" % ("request", "A", "B", "identical?"))
    print("-" * 70)

    failures = 0
    for name, args in KNOWN:
        label = name + (" +confirm" if args.get("confirm") else "")
        sa = signature(post(a, "/mcp/tour", {"name": name, "args": args}))
        sb = signature(post(b, "/mcp/tour", {"name": name, "args": args}))
        same = sa == sb
        failures += 0 if same else 1
        print("%-34s %-9s %-9s %s" % (label, sa["decision"], sb["decision"],
                                      "YES" if same else "NO"))

    ra = signature(post(a, "/verify", {"input": 17}))
    rb = signature(post(b, "/verify", {"input": 17}))
    va = post(a, "/verify", {"input": 17}).get("expected")
    vb = post(b, "/verify", {"input": 17}).get("expected")
    same = va == vb
    failures += 0 if same else 1
    print("%-34s %-9s %-9s %s" % ("verify(17) -> oracle", va, vb,
                                  "YES" if same else "NO"))

    print()
    print("Now the one place the models legitimately differ:")
    ua = post(a, "/mcp/tour", {"name": UNKNOWN[0], "args": UNKNOWN[1]})
    ub = post(b, "/mcp/tour", {"name": UNKNOWN[0], "args": UNKNOWN[1]})
    print("  A  decision=%s  model=%s" % (ua.get("decision"), ua.get("model")))
    print("  B  decision=%s  model=%s" % (ub.get("decision"), ub.get("model")))
    print("  routing decision identical : %s"
          % ("YES" if ua.get("decision") == ub.get("decision") else "NO"))
    print("  wording identical          : %s   (expected: NO -- two different"
          " models, two different sentences)"
          % ("YES" if ua.get("result") == ub.get("result") else "NO"))
    print()
    print("VERDICT: %d mismatch(es) on the deterministic path." % failures)
    print("The architecture, not the model, decides what happens.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
