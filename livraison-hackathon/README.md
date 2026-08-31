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
