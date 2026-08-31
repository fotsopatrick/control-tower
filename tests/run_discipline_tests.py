import json
import subprocess
import time
from test_reasoning_discipline import CASES

def evaluate_case(case):
    # Prompting le SGRM
    prompt = f"CONTEXTE:\n{case['context']}\n\nDEMANDE:\n{case['request']}\n\nRETOURNE UNIQUEMENT LA RÉPONSE."
    
    t0 = time.time()
    # Appel du sélecteur/LLM
    res = subprocess.run(
        ["python3", "/home/orel/SGRM_PROJECT/sgrm_selector.py"], 
        input=prompt, capture_output=True, text=True
    )
    t1 = time.time() - t0
    
    response = res.stdout
    forbidden_hits = [term for term in case["forbidden"] if term.lower() in response.lower()]
    
    return {
        "pass": len(forbidden_hits) == 0,
        "forbidden_hits": forbidden_hits,
        "latency": t1,
        "response": response
    }

print("| Test | PASS | FAIL | Contamination |")
print("|------|------|------|---------------|")
for case in CASES:
    res = evaluate_case(case)
    status = "PASS" if res["pass"] else "FAIL"
    print(f"| {case['name']} | {status} | {'FAIL' if not res['pass'] else ''} | {res['forbidden_hits']} |")
