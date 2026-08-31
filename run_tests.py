"""Reproducible check: the reasoner and the independent oracle must agree.

Runs from the repository root, with no absolute paths and no hand-written
expected values. Exits non-zero on the first disagreement.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ORACLE = ROOT / "local_tour" / "independent_oracle.py"
sys.path.insert(0, str(ROOT))
from sgrm_core import apply_procedure  # noqa: E402

STEPS = ["op_q9", "op_k7", "op_m2"]
INPUTS = [17, 20, 100, 0, -3]


def oracle(value):
    proc = subprocess.run([sys.executable, str(ORACLE), str(value)],
                          capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError("oracle refused input %s" % value)
    return int(proc.stdout.strip())


def main():
    failures = 0
    print("input | reasoner | oracle | verdict")
    print("------+----------+--------+--------")
    for value in INPUTS:
        actual, _ = apply_procedure(value, STEPS)
        expected = oracle(value)
        ok = actual == expected
        failures += 0 if ok else 1
        print("%5d | %8d | %6d | %s" % (value, actual, expected,
                                        "PASS" if ok else "FAIL"))
    print()
    print("%d input(s) checked, %d failure(s)" % (len(INPUTS), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
