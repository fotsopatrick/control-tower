#!/usr/bin/env bash
# Same router, but the fallback is a self-hosted Qwen instead of Google Gemini.
cd /home/orel/SGRM_PROJECT
export PYTHONPATH=/home/orel/SGRM_PROJECT
export FALLBACK=local
export LOCAL_MODEL_URL=http://20.97.179.141:11434
export LOCAL_MODEL_NAME=qwen2.5:7b
exec /home/orel/.venv-sgrm-demo/bin/python3 -m uvicorn gcp_router.main:app --host 127.0.0.1 --port 8090
