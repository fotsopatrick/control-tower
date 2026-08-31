# Alice — the bonus: where this architecture actually came from

Alice is not part of the judged submission. She is included because she is the
reason the Control Tower is shaped the way it is, and because the claim
"a deterministic front door saves real money" is not a thought experiment here:
it started as a constraint, not as a design choice.

## The origin

We ran out of credit on a paid model. Not metaphorically — the balance hit
zero mid-project. The only way to keep working was a model that costs nothing,
which meant a model running on our own hardware.

That machine is Alice. Her brain is a single file on disk,
`qwen2.5-3b-instruct` (2.1 GB), served by `llama.cpp` on ordinary hardware,
no datacenter GPU. She is slow: roughly 29 tokens/second reading a prompt,
8 tokens/second writing an answer. A hosted model beats her comfortably.

But she costs nothing per call, and something that costs nothing can run
permanently.

## What the constraint taught us

When a model is expensive, you put it first and pay for every question.
When a model is *slow*, you cannot do that. You are forced to ask, before
every request: **do I already have this answer?**

So Alice's router asks four questions, in this order:

1. **Does the living map know?** — the map is a survey of what actually exists.
   If the request matches, answer without reasoning at all.
2. **Does memory know?** — a small database of procedures already learned.
3. **Can a tool do it?** — reading an image, listing a directory. These are
   gestures, not reasoning.
4. **Only then, wake the model.**

None of those four steps is a new idea. What was new was being *forced* to put
them in that order. With credit in the bank there had been no reason to.

The Control Tower's deterministic front door is the same cascade, written a
second time, on different hardware, for a different reason — measurement rather
than poverty. Two unrelated constraints producing the same shape is worth
noticing.

## What she can do that the Tower cannot yet

Alice can change her own engine at runtime: `auto`, `azure`, or `qwen`
(`routeur.py:choisir_modele`, exposed at `GET/POST /api/v1/modele`). Verified
live on 31 August 2026: the endpoint answers `{"force": false, "modele": "qwen"}`.

## What is in this folder, and what is not

Included — the reasoning, 2 406 lines:

| file | role |
|---|---|
| `routeur.py` | the cascade: map → memory → tools → model |
| `memory.py` | short-term memory (SQLite) |
| `adaptateur_carte.py` | reads the living map |
| `knowledge.py` | document ingestion and retrieval |
| `guardrails.py` | deterministic safety checks |
| `alice_gate.py` | the HTTP front door |
| `chat_backend.py` | the chat endpoint |

Deliberately **not** included: the databases (they are her memory, i.e. real
conversations), the logs, and the ingested documents. A code contribution does
not require publishing someone's private data, and none of it would help a
reviewer understand the architecture.

The one hard-coded host address has been replaced by `ALICE_BRAIN_URL`.

## Honest limits

Alice is a 3-billion-parameter model. On open questions, long reasoning, or
fine shades of language, she loses to a hosted model — clearly. That is not
the comparison being made. The claim is narrower and it is measurable: a large
share of daily agent work is *lookup*, not reasoning, and for lookup a large
model is an expensive luxury.

How large a share exactly, we have not measured yet. That is the next
experiment, and we would rather say so than guess.
