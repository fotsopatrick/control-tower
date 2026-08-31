#!/usr/bin/env bash
# Same router, but the fallback is a self-hosted model instead of Google Gemini.
# Point LOCAL_MODEL_URL at your own Ollama instance before running.
cd /home/orel/SGRM_PROJECT
export PYTHONPATH=/home/orel/SGRM_PROJECT
export FALLBACK=local
export LOCAL_MODEL_URL="${LOCAL_MODEL_URL:-http://localhost:11434}"
export LOCAL_MODEL_NAME="${LOCAL_MODEL_NAME:-qwen2.5:7b}"
exec /home/orel/.venv-sgrm-demo/bin/python3 -m uvicorn gcp_router.main:app --host 127.0.0.1 --port 8090
