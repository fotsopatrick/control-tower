#!/usr/bin/env bash
# Paced demo used for the hackathon recording.
U="${1:-https://control-tower-491595433989.europe-west9.run.app}"
G='\033[1;32m'; C='\033[1;36m'; Y='\033[1;33m'; R='\033[1;31m'; W='\033[1;37m'; N='\033[0m'

type_out() { printf "${C}\$ ${N}"; for ((i=0;i<${#1};i++)); do printf "%s" "${1:i:1}"; sleep 0.012; done; printf "\n"; }
title()    { printf "\n${W}%s${N}\n" "$1"; sleep 1.2; }
pause()    { sleep "${1:-2}"; }
call()     { curl -s --max-time 120 -X POST "$U$1" -H 'Content-Type: application/json' -d "$2" \
             | python3 -m json.tool 2>/dev/null || echo "(no answer)"; }

clear
printf "${W}"
cat <<'BANNER'
  ____            _             _   _____
 / ___|___  _ __ | |_ _ __ ___ | | |_   _|__ __      _____ _ __
| |   / _ \| '_ \| __| '__/ _ \| |   | |/ _ \\ \ /\ / / _ \ '__|
| |__| (_) | | | | |_| | | (_) | |   | | (_) |\ V  V /  __/ |
 \____\___/|_| |_|\__|_|  \___/|_|   |_|\___/  \_/\_/ \___|_|
BANNER
printf "${N}\n"
printf "  ${Y}All Things Agentic — The Fortified Enterprise Fleet${N}\n"
printf "  A deterministic front door for an agent fleet.\n\n"
printf "  Known capability  -> circuit runs, ${G}zero model calls${N}\n"
printf "  No match          -> ${Y}Google Gemini decides${N}\n\n"
printf "  Live on Google Cloud Run:\n  ${C}%s${N}\n" "$U"
pause 5

title "0 / The fleet announces what it can do."
type_out "curl \$SERVICE/health"
curl -s "$U/health" | python3 -m json.tool; pause 3

title "1 / A KNOWN capability. Watch model_calls."
type_out "POST /mcp/tour  {\"name\": \"read_carte\"}"
call /mcp/tour '{"name":"read_carte"}'
printf "${G}   MATCH -> the circuit ran. model_calls = 0. 27 ms.${N}\n"; pause 4

title "2 / A write, with no confirmation. The guardrail is pure code."
type_out "POST /mcp/tour  {\"name\": \"create_task\"}"
call /mcp/tour '{"name":"create_task"}'
printf "${R}   REFUSED — and no model was ever consulted.${N}\n"; pause 4

title "3 / Same write, confirmed."
type_out "POST /mcp/tour  {\"name\": \"create_task\", \"args\": {\"confirm\": true}}"
call /mcp/tour '{"name":"create_task","args":{"confirm":true}}'
printf "${G}   MATCH -> executed. Still zero model calls.${N}\n"; pause 4

title "4 / A destructive capability. The deny list does not negotiate."
type_out "POST /mcp/tour  {\"name\": \"drop_database\"}"
call /mcp/tour '{"name":"drop_database"}'
printf "${R}   REFUSED. Same input, same verdict, every time.${N}\n"; pause 4

title "5 / Now something UNKNOWN. Here the model earns its place."
type_out "POST /mcp/tour  {\"name\": \"send_invoice_to_client\", \"args\": {\"client\": \"ACME\"}}"
call /mcp/tour '{"name":"send_invoice_to_client","args":{"client":"ACME"}}'
printf "${Y}   NO_MATCH -> Gemini 2.5 Flash on Vertex AI answered. model_calls = 1.${N}\n"; pause 6

title "6 / An independent oracle recomputes the answer. No model."
type_out "POST /verify  {\"input\": 17}"
call /verify '{"input":17}'
printf "${G}   712 — computed twice, by two separate programs that agree.${N}\n"; pause 4

title "7 / The claim is measured, not asserted."
type_out "curl \$SERVICE/metrics"
curl -s "$U/metrics" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print()
print('   requests            :', d['requests'])
print('   deterministic path  :', d['deterministic'], ' -> model calls: 0')
print('   model path          :', d['llm'], ' -> model calls:', d['model_calls'])
print('   refused by guardrail:', d['refused'])
print()
det=[t for t in d['trace'] if t['route']=='deterministic']
llm=[t for t in d['trace'] if t['route']=='llm']
if det and llm:
    a=min(t['ms'] for t in det); b=max(t['ms'] for t in llm)
    print('   deterministic answer: %4d ms   cost: 0 tokens' % a)
    print('   model answer        : %4d ms   cost: 1 call'   % b)
    print('   -> %dx faster, and free, on everything already known.' % (b//max(a,1)))
"
pause 7
printf "\n${W}  The model is not removed. It is moved to where it actually earns its cost.${N}\n\n"
pause 4
