# Control Tower — a deterministic front door for an agent fleet

**Hackathon: All Things Agentic — track: The Fortified Enterprise Fleet**

## What this buys — and how it was measured

The Control Tower exists to make an agent fleet **produce faster without
producing garbage**. So this hackathon is not the product. It is the
**measurement**: a hard deadline, a cold start, one person.

Registered 29 August. Submitted 31 August. In that window this repository
gained a deterministic router deployed on Cloud Run, guardrails that refuse in
pure code, delegation across specialised sub-agents, an independent oracle,
and an audit script that **fails the build** when this README claims something
the disk does not support.

**78 files. 8,325 lines of Python and shell. Two days.**

*(Snapshot taken 31 August 2026, 20:00 Europe/Paris. The count moves as the
repository moves — that is why the command is printed below rather than the
number alone.)*

Counted, not asserted — the command is in the repository:

```bash
find . -type f \( -name '*.py' -o -name '*.sh' \) -not -path './.git/*' \
     -newermt '2026-08-29' -exec cat {} + | wc -l
```

The friction removed is not "fewer model calls". That is the mechanism, not the
gain. The friction removed is **the human who no longer has to re-read every
action before it runs** — because the gate that matters does not depend on a
model's mood. Determinism is what makes autonomy *grantable at scale*.

## The question

Can a large share of an agent's work be moved out of probabilistic reasoning
and into deterministic mechanisms — without losing the model when it is
genuinely needed?

Control Tower answers a **known** capability by running a circuit, with **zero
model calls**. It calls **Google Gemini** only when nothing in the registry
matches. Both counts are published at `/metrics`, so the claim is a
measurement, not a sentence in a README.

## Mandatory disclosures

**Pre-existing work.** The Living Map discovery mechanism and the Circuit
orchestration model come from an earlier experimental project (an Odoo-based
control tower). The guardrail philosophy and the circuit registry are derived
from that prior work.

**Built during the submission period.** The deterministic router in
`gcp_router/`, the fallback path through the Google GenAI SDK, the independent
oracle wiring, the `/metrics` observability, the Cloud Run deployment, and the
audit script `audit_sgrm_hackathon.py` that checks this repository against its
own claims.

**Honest limitation.** The SGRM (Small General Reasoning Model) is at prototype
stage. Today it selects among hand-written strategies and executes them
deterministically; it is not a trained model. `sgrm_selector.py` queries a
local Qwen instance for strategy selection — that is a separate experiment from
the Gemini fallback path and is not required by the demo.

## Technology

- **Model**: Google Gemini via the `google-genai` SDK (the router tries
  `gemini-3.5-flash` first — the mandatory minimum for this hackathon — then
  falls back to older flash models; the list is configurable with `GEMINI_MODELS`)
- **Serving**: FastAPI on Google Cloud Run
- **Verification**: an independent oracle program, no model involved

## Architecture

See [`docs/architecture-diagram.md`](docs/architecture-diagram.md).




## Delegation to specialised sub-agents

A fleet is not one agent wearing many hats. Each agent in this tower has a
written specification, a declared scope, and an engine — **9 of the 21 are bound
to no model at all**. When a request is broader than one capability, the control
plane splits it and hands each piece to the agent whose specification covers it.

```bash
curl -s -X POST $S/delegate -H 'Content-Type: application/json' -d '{
  "request": "run the regression tests and audit the secrets then review the wording and publish the article"
}'
```

**You must see** the request cut into **4 pieces**, handed to **4 different
agents**, with this outcome:

| agent | role | engine | piece | outcome |
|---|---|---|---|---|
| Jimmy | the test bench | none | run the regression tests | done |
| Victor | security | none | audit the secrets | done |
| Lois | review | none | review the wording | done |
| Chloe | daily assistant | smolagents | publish the article | **refused** |

`handled_without_any_model: 3` — three of the four pieces never touched a model.

And the refusal names its own cause:
`"Chloe may not publish: its specification grants may_publish = false"`.

**Separation of concerns is enforced in code, not suggested in a prompt.** An
agent is never handed work outside its declared scope, and a sub-agent that
fails marks only its own piece — the remaining pieces continue. That is what
failure-tolerant routing means when a worker loops or returns nonsense.

Press **Delegate to sub-agents** on `$S/demo` to watch it happen.

## Asynchronous batch work — where the saving becomes obvious

`POST /batch` takes a pile of agent requests, returns a job id in about 100 ms,
and does the work in the background. `GET /batch/{id}` reports progress and the
split between paths. This is the shape the track asks for: hand over the heavy
lifting and walk away.

Measured on the deployed service, 200 mixed requests (mostly known
capabilities, some writes, some denied, some genuinely unknown):

| | count | median | total |
|---|---|---|---|
| answered by a circuit | 180 | **9 ms** | 70 s |
| refused by a guardrail | 10 | 0 ms | 0 s |
| escalated to Gemini 3.5 | 10 | 5 899 ms | 121 s |

**10 model calls instead of 200 — a 95% reduction.** That number does not
depend on hardware, network or load: it is a count, not a timing.

The latency ratio (655x on medians) does depend on those things, and it moved
from 8x to 655x once the living map was parsed once instead of on every
request. We report the median because the mean is inflated by warm-up and by
requests contending inside a single container.

### The circuit is real work, not a placeholder

`read_carte` reads the **living map** — a survey of what actually exists in the
tower: 478 entries across 9 zones (services, containers, volumes, agents,
circuits, tools). It answers summaries, searches and per-zone listings. The
shipped copy has every host address and identifier redacted.

That matters: the claim "a deterministic path can replace the model" is only
worth something if the deterministic path is doing work a model would otherwise
have been asked to do.

## Bonus: Alice — where this architecture came from

The deterministic cascade in this project was not designed on a whiteboard. It
was forced on us when the credit on a paid model ran out and the only option
left was a model running on our own hardware. That machine is Alice, and her
router asks the same four questions in the same order: map, memory, tools,
then — only then — the model.

Her reasoning code is in [`alice/`](alice/), with the full story, the measured
numbers, and an explicit list of what was deliberately left out (her databases
and logs, which are private conversations). She is offered as context, not as
part of the judged submission.

## Setup / spin-up

```bash
git clone <this repo> && cd SGRM_PROJECT
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY=<your Gemini API key>   # only needed for the fallback path
uvicorn gcp_router.main:app --host 0.0.0.0 --port 8080
```

Then run the demo:

```bash
./demo_flight.sh                      # local
./demo_flight.sh https://<cloud-run-url>   # deployed
```

Deploy to Cloud Run:

```bash
gcloud run deploy control-tower --source . --region europe-west9 \
  --allow-unauthenticated --set-env-vars GOOGLE_API_KEY=<key>
```


## Reproducible testing — type this, you must see that

Every command below runs against the live service. No credentials needed.
`$S` is the deployed URL:

```bash
S=https://control-tower-491595433989.europe-west9.run.app
```

### 1. A known capability costs nothing

```bash
curl -s -X POST $S/mcp/tour -H 'Content-Type: application/json' \
     -d '{"name":"read_carte"}'
```

**You must see** `"decision":"MATCH"`, `"model_calls":0`, and a summary of the
living map beginning `LIVING MAP — surveyed`, listing **478 entries across 9
zones**. If `model_calls` is anything but `0`, the central claim of this project
is false.

### 2. The guardrail refuses, and says why

```bash
curl -s -X POST $S/mcp/tour -H 'Content-Type: application/json' \
     -d '{"name":"create_task"}'
```

**You must see** `"decision":"REFUSED"` and
`"reason":"write capability requires args.confirm = true"`.

```bash
curl -s -X POST $S/mcp/tour -H 'Content-Type: application/json' \
     -d '{"name":"drop_database"}'
```

**You must see** `"decision":"REFUSED"` and `"on the deny list"`.

### 3. An unknown capability reaches Gemini 3.5

```bash
curl -s -X POST $S/mcp/tour -H 'Content-Type: application/json' \
     -d '{"name":"send_invoice_to_client","args":{"client":"ACME"}}'
```

**You must see** `"decision":"NO_MATCH"`, `"model":"vertex/gemini-3.5-flash"`,
and `"model_calls":1`. Takes about 6 seconds — that is the model thinking.

### 4. The independent oracle

```bash
curl -s -X POST $S/verify -H 'Content-Type: application/json' -d '{"input":17}'
```

**You must see** `{"input":17,"expected":712,"model_calls":0}`. The value is
recomputed by a separate program (`local_tour/independent_oracle.py`); it is
never read from a stored answer.

### 5. The saving, at scale, in the background

```bash
curl -s -X POST $S/batch -H 'Content-Type: application/json' \
     -d "{\"requests\":[$(for i in $(seq 1 190); do printf '{"name":"read_carte"},'; done)$(for i in $(seq 1 9); do printf '{"name":"unknown_%d"},' $i; done){"name":"unknown_10"}]}"
```

**You must see** a `job_id` returned in well under a second — the caller does
not wait. Then poll it:

```bash
curl -s $S/batch/<job_id>
```

**You must see** `state: finished`, `deterministic: 190`, `llm: 10`,
`model_calls: 10`, and `share_without_model` around **95**.
Ten model calls for two hundred requests.

Or press **Hand over 200 requests** on `$S/demo` and watch the counter climb.

### 6. Locally, without any network

```bash
python3 run_tests.py        # reasoner vs independent oracle, 5 inputs
python3 sgrm_core.py        # full arithmetic trace, exits non-zero on disagreement
python3 audit_sgrm_hackathon.py .   # checks this README against the files on disk
```

**You must see** `5 input(s) checked, 0 failure(s)`, then `verdict = AGREE`,
then `11 PASS / 0 WARN / 0 FAIL` and `VERDICT : CONFORME`.

That last script is deliberately hostile to its own repository: it fails the
build when a claim made here is not corroborated by a file. It has already
caught a fabricated Gemini integration in an earlier version of this project.

### 7. Same answers, two different models

```bash
python3 preuve_deux_modeles.py $S http://localhost:8090
```

Requires a second router whose fallback is a self-hosted model
(`./lancer_routeur_local.sh` with `LOCAL_MODEL_URL` pointing at your Ollama).
**You must see** `0 mismatch(es) on the deterministic path` — every routing
decision, guardrail verdict and computed value identical, whichever model backs
the fallback.

## What the demo shows

| Step | Request | Expected | Model calls |
|---|---|---|---|
| 1 | `read_carte` | circuit runs | **0** |
| 2 | `create_task` without `confirm` | guardrail refuses | 0 |
| 3 | `create_task` with `confirm` | circuit runs | 0 |
| 4 | `drop_database` | refused, deny-list | 0 |
| 5 | `send_invoice_to_client` (unknown) | Gemini answers | 1 |
| 6 | `/verify` on 17 | oracle returns 712 | 0 |

## Checking the repository against its own claims

```bash
python3 audit_sgrm_hackathon.py .
```

The script fails the build if a claim in this README is not corroborated by the
files on disk. It was written to catch exactly the kind of drift that produced
an earlier version of this project claiming a Gemini integration that the code
never actually performed.

## Reproducibility

`sgrm_core.py` prints its full arithmetic trace and exits non-zero when the
independent oracle disagrees with it. No expected value in this repository is
written by hand.
