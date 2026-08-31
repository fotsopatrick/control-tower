# Control Tower — a deterministic front door for an agent fleet

**Hackathon: All Things Agentic — track: The Fortified Enterprise Fleet**

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
  `gemini-2.5-flash` first; the model list is configurable with `GEMINI_MODELS`)
- **Serving**: FastAPI on Google Cloud Run
- **Verification**: an independent oracle program, no model involved

## Architecture

See [`docs/architecture-diagram.md`](docs/architecture-diagram.md).



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
