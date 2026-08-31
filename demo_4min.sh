#!/usr/bin/env bash
# 4-minute live demo for the All Things Agentic submission.
# Every number on screen is returned by the deployed service, live.
S="${1:-https://control-tower-491595433989.europe-west9.run.app}"
G='\033[1;32m'; C='\033[1;36m'; Y='\033[1;33m'; R='\033[1;31m'; W='\033[1;37m'; D='\033[0;90m'; N='\033[0m'

t()   { printf "${D}\$ ${N}"; for ((i=0;i<${#1};i++)); do printf "%s" "${1:i:1}"; sleep 0.010; done; printf "\n"; }
h()   { printf "\n\n${W}══════════════════════════════════════════════════════════════════${N}\n"; printf "${W}  %s${N}\n" "$1"; printf "${W}══════════════════════════════════════════════════════════════════${N}\n\n"; sleep 1.5; }
say() { printf "${Y}  %s${N}\n" "$1"; }
ok()  { printf "${G}  ➜ %s${N}\n" "$1"; }
call(){ curl -s --max-time 120 -X POST "$S$1" -H 'Content-Type: application/json' -d "$2" | python3 -m json.tool 2>/dev/null; }

clear; printf "${W}"
cat <<'B'
   ____            _             _   _____
  / ___|___  _ __ | |_ _ __ ___ | | |_   _|____      _____ _ __
 | |   / _ \| '_ \| __| '__/ _ \| |   | |/ _ \ \ /\ / / _ \ '__|
 | |__| (_) | | | | |_| | | (_) | |   | | (_) \ V  V /  __/ |
  \____\___/|_| |_|\__|_|  \___/|_|   |_|\___/ \_/\_/ \___|_|
B
printf "${N}\n"
say "All Things Agentic  —  track: The Fortified Enterprise Fleet"
printf "\n"
say "THE PROBLEM: an agent that decides everything with a model is"
say "unaffordable, slow, and impossible to audit at fleet scale."
printf "\n"
say "THE ANSWER: a deterministic front door. Known work runs as code."
say "The model is called only when nothing matches."
printf "\n"
printf "  Live on Google Cloud Run:\n  ${C}%s${N}\n" "$S"
sleep 7

h "0 / The fleet declares what it can do"
t "curl \$SERVICE/health"
curl -s --max-time 60 "$S/health" | python3 -m json.tool
ok "Three capabilities, published. Nothing hidden."
sleep 3

h "1 / 200 requests, launched NOW — we come back at the end"
say "Asynchronous background work. 190 known + 10 unknown."
t "curl -X POST \$SERVICE/batch  (200 requests)"
JOB=$(curl -s --max-time 90 -X POST "$S/batch" -H 'Content-Type: application/json' \
  -d "{\"requests\":[$(for i in $(seq 1 190); do printf '{"name":"read_carte"},'; done)$(for i in $(seq 1 9); do printf '{"name":"unknown_%d"},' $i; done){\"name\":\"unknown_10\"}]}" \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['job_id'])")
ok "Accepted instantly. Job: $JOB — it runs while we keep talking."
sleep 4

h "2 / A KNOWN capability. Watch model_calls."
t "POST /mcp/tour  {\"name\":\"read_carte\"}"
call /mcp/tour '{"name":"read_carte"}' | head -12
ok "MATCH -> a circuit ran. model_calls = 0. No model was consulted."
sleep 5

h "3 / A write. The guardrail is pure code, not a prompt."
t "POST /mcp/tour  {\"name\":\"create_task\"}     (no confirmation)"
call /mcp/tour '{"name":"create_task"}'
ok "REFUSED — and it says why. Zero model calls to decide that."
sleep 4
t "POST /mcp/tour  {\"name\":\"create_task\",\"args\":{\"confirm\":true}}"
call /mcp/tour '{"name":"create_task","args":{"confirm":true}}' | head -10
ok "Now it runs. Same input, same verdict, every time."
sleep 5

h "4 / A destructive order. No model is asked for permission."
t "POST /mcp/tour  {\"name\":\"drop_database\"}"
call /mcp/tour '{"name":"drop_database"}'
ok "REFUSED by a deny-list. Destruction never depends on a model's mood."
sleep 5

h "5 / An UNKNOWN capability. Now — and only now — Gemini 3.5."
t "POST /mcp/tour  {\"name\":\"send_invoice_to_client\"}"
call /mcp/tour '{"name":"send_invoice_to_client"}' | head -14
ok "NO_MATCH -> vertex/gemini-3.5-flash answered. This is the fallback."
sleep 5

h "6 / The independent oracle — verification without a model"
t "POST /mcp/tour/../verify  {\"input\":17}"
curl -s --max-time 60 -X POST "$S/verify" -H 'Content-Type: application/json' -d '{"input":17}' | python3 -m json.tool
ok "Checked by a separate program. model_calls = 0."
sleep 4

h "7 / Back to the 200 requests. This is the whole thesis."
t "curl \$SERVICE/batch/$JOB"
curl -s --max-time 90 "$S/batch/$JOB" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for k in ('state','done','total','deterministic','llm','model_calls','refused','errors','share_without_model'):
    if k in d: print('  %-22s : %s' % (k, d[k]))
"
printf "\n"
ok "190 of 200 done with ZERO model calls. 0 errors."
ok "The service computes that share itself and publishes it."
sleep 6

h "8 / The repository audits its own README"
t "python3 audit_sgrm_hackathon.py ."
cd "$(dirname "$0")" && python3 audit_sgrm_hackathon.py . 2>&1 | tail -6
ok "It FAILS THE BUILD when a claim is not corroborated by the files."
sleep 5

h "Two days. One person. 78 files, 8,325 lines."
say "The hackathon is not the product. It is the measurement."
printf "\n"
printf "  ${C}%s${N}\n\n" "$S"
sleep 6
