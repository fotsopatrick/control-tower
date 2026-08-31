"""SGRM core: pick a strategy, run it, then let an independent oracle judge.

The result is never written by hand. It is computed by the procedure, and the
oracle recomputes it separately. If the two disagree the run fails -- that
disagreement is exactly what an oracle is for.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ORACLE = ROOT / "local_tour" / "independent_oracle.py"

OPS = {"op_k7": (3, 7), "op_m2": (5, 2), "op_q9": (2, 11)}


def apply_procedure(value, steps):
    """The 'sequential' strategy: chain the operators, keeping the trace."""
    trace = []
    for step in steps:
        a, b = OPS[step]
        new = value * a + b
        trace.append("%d -> %s: %d*%d+%d = %d" % (value, step, value, a, b, new))
        value = new
    return value, trace


def oracle_expected(value):
    proc = subprocess.run([sys.executable, str(ORACLE), str(value)],
                          capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError("oracle refused the input")
    return int(proc.stdout.strip())


def sgrm_reason(case):
    if case["strategy"] != "sequential":
        raise ValueError("unknown strategy: %s" % case["strategy"])
    start = int(case["problem"].rsplit(" ", 1)[-1])
    result, trace = apply_procedure(start, case["steps"])
    expected = oracle_expected(start)
    return {"input": start, "result": result, "expected": expected,
            "agrees": result == expected, "trace": trace, "model_calls": 0}


if __name__ == "__main__":
    case = json.load(open(ROOT / "sgrm_dataset.json"))[0]
    out = sgrm_reason(case)
    for line in out["trace"]:
        print("  " + line)
    print("result  = %d" % out["result"])
    print("oracle  = %d" % out["expected"])
    print("verdict = %s" % ("AGREE" if out["agrees"] else "DISAGREE"))
    print("model calls used = %d" % out["model_calls"])
    sys.exit(0 if out["agrees"] else 1)
