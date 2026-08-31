# SGRM prototype — what was actually measured

Corrected on 31 August 2026. An earlier version of this file claimed an
expected value of `5468` and a "Qwen accuracy of 85%". Neither was supported:
the independent oracle computes `712` for the same input, and no script in
this repository ever measured Qwen's accuracy. Both claims are removed rather
than restated.

## 1. What the SGRM is today

A strategy selector plus a set of hand-written circuits. It is **not** a
trained model. It picks among strategies a human wrote, then executes them
deterministically.

## 2. Reference case

Procedure `[op_q9, op_k7, op_m2]` applied to `17`.

| | value | model calls |
|---|---|---|
| reasoner (`sgrm_core.py`) | 712 | 0 |
| independent oracle | 712 | 0 |
| verdict | AGREE | — |

Reproduce with `python3 run_tests.py`. It checks five inputs
(17, 20, 100, 0, -3) and exits non-zero on any disagreement.

## 3. Routing, measured on the deployed service

Repeat with `python3 mesurer_honnetement.py <service-url>`.

| path | runs | median | range | model calls |
|---|---|---|---|---|
| deterministic | 15 | 102 ms | 78 – 195 ms | **0** |
| Gemini fallback | 6 | 7 627 ms | 5 736 – 19 763 ms | 6 |

The latency ratio moves between runs and depends on which clock is used
(inside the server, or end to end from the client). The zero on the
deterministic path does not move. That is the result worth quoting.

## 4. Honest limits

- The circuit used in the demo prints one line. A circuit doing real work
  would be slower, so the latency ratio is an upper bound.
- No accuracy comparison against a hosted model has been run. Any such number
  would have to be measured first.
- Error handling on the fallback path is minimal.
