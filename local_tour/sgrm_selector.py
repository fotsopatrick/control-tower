import json
import urllib.request
import subprocess
import time

def select_strategy(problem):
    prompt = f"Choose strategy ['séquentiel', 'déduction'] for problem: '{problem}'. Output only the word."
    data = json.dumps({"model": "qwen2.5:7b", "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request("http://20.97.179.141:11434/api/generate", data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        return res["response"].strip().lower()

# Benchmark
problem = "Appliquer procédure [op_q9, op_k7, op_m2] sur 17"
t0 = time.time()
strategy = select_strategy(problem)
t_model = time.time() - t0

# Exécution du circuit
if strategy == "séquentiel":
    res = subprocess.run(["python3", "/root/.gemini/tmp/ssh/local_tour/circuits/apply_procedure.py"], capture_output=True, text=True)
    resultat = res.stdout.strip()
    verif = "PASS" if resultat == "712" else "FAIL"
    print(f"Modèle: Qwen 2.5 7B | Temps: {t_model:.4f}s | Stratégie: {strategy} | Résultat: {resultat} | Vérificateur: {verif}")
else:
    print(f"Échec sélection stratégie: {strategy}")
