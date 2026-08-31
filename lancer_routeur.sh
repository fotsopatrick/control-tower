#!/usr/bin/env bash
# Starts the Control Tower router locally on port 8080.
cd /home/orel/SGRM_PROJECT
export PYTHONPATH=/home/orel/SGRM_PROJECT
exec /home/orel/.venv-sgrm-demo/bin/python3 -m uvicorn gcp_router.main:app --host 127.0.0.1 --port 8080
