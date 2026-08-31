# Architecture diagram — Control Tower

```
                          ┌──────────────────────────┐
       agent request ───► │  DETERMINISTIC FRONT DOOR │
                          │      (gcp_router)         │
                          └────────────┬──────────────┘
                                       │
                          ┌────────────▼──────────────┐
                          │  GUARDRAILS (pure code)   │   deny-list,
                          │  same input, same verdict │   write-confirm
                          └────────────┬──────────────┘
                                       │ allowed
                    ┌──────────────────┴───────────────────┐
                    │                                      │
        capability in registry?                    no match in registry
                    │                                      │
                    ▼                                      ▼
        ┌───────────────────────┐              ┌────────────────────────┐
        │  CIRCUIT EXECUTED     │              │  GOOGLE GEMINI         │
        │  local_tour/circuits  │              │  (google-genai SDK)    │
        │  model calls  =  0    │              │  model calls  =  1     │
        └───────────┬───────────┘              └───────────┬────────────┘
                    │                                      │
                    └──────────────────┬───────────────────┘
                                       ▼
                          ┌──────────────────────────┐
                          │  INDEPENDENT ORACLE      │  recomputes the answer
                          │  /verify — no model      │  without the model
                          └────────────┬─────────────┘
                                       ▼
                          ┌──────────────────────────┐
                          │  OBSERVABILITY  /metrics │  deterministic vs llm,
                          │  per-request trace       │  measured, not claimed
                          └──────────────────────────┘
```

## Why this shape

The hypothesis under test is that a large share of an agent's work can be moved
out of probabilistic reasoning and into deterministic mechanisms. The router
therefore answers a known capability **without calling any model at all**, and
falls back to Gemini only when nothing in the registry matches.

`GET /metrics` publishes the two counters side by side, so the claim
"zero model calls on known capabilities" is a measurement anyone can reproduce,
not a sentence in a README.

The oracle is deliberately a separate program: it recomputes the expected value
from the operator table alone. When the reasoner and the oracle disagree, the
run is marked failed. A checker that shares code with the thing it checks is
not a checker.
