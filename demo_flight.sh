#!/usr/bin/env bash
# Control Tower demo flight.
#   ./demo_flight.sh                      -> against http://127.0.0.1:8080
#   ./demo_flight.sh https://your.run.app -> against a deployed service
set -u
BASE="${1:-http://127.0.0.1:8080}"
say() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
post() { curl -s -X POST "$BASE$1" -H 'Content-Type: application/json' -d "$2"; echo; }

say "0. Service health"
curl -s "$BASE/health"; echo

say "1. Known capability -> circuit runs, ZERO model calls"
post /mcp/tour '{"name":"read_carte"}'

say "2. Write without confirmation -> guardrail refuses"
post /mcp/tour '{"name":"create_task"}'

say "3. Write with confirmation -> circuit runs"
post /mcp/tour '{"name":"create_task","args":{"confirm":true}}'

say "4. Deny-listed capability -> refused, no model consulted"
post /mcp/tour '{"name":"drop_database"}'

say "5. Unknown capability -> falls back to Google Gemini"
post /mcp/tour '{"name":"send_invoice_to_client","args":{"client":"ACME"}}'

say "6. Independent oracle recomputes the answer, no model"
post /verify '{"input":17}'

say "7. Counters: deterministic vs model calls"
curl -s "$BASE/metrics"; echo
