import subprocess
import json
import time

def run_case(problem, expected_strategy):
    t0 = time.time()
    # On simule l'exécution du sélecteur
    res = subprocess.run(["python3", "/root/.gemini/tmp/ssh/local_tour/sgrm_selector.py"], capture_output=True, text=True)
    t_model = time.time() - t0
    
    # Analyse de sortie
    out = res.stdout.strip()
    return {"time": t_model, "output": out}

# Cas 1: Nominal (répétition)
print(f"Nominal: {run_case('Appliquer procédure [op_q9, op_k7, op_m2] sur 17', 'séquentiel')}")

# Cas 2: Stratégie invalide (pour forcer erreur)
# On simule un prompt qui forcera une mauvaise réponse
# Comme le modèle est Qwen, on peut lui donner un prompt biaisé
