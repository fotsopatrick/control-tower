import subprocess
import json
import time

def run_test(problem, mock_response=None):
    # Appel simplifié pour simuler le comportement du sélecteur
    # On exécute le sélecteur réel
    res = subprocess.run(["python3", "/root/.gemini/tmp/ssh/local_tour/sgrm_selector.py"], capture_output=True, text=True)
    return res.stdout.strip()

# Tests
print("--- TEST MATRICE ---")
print(f"Nominal: {run_test('Appliquer procédure')}")

# Test Déterminisme (3 runs)
print("--- TEST DÉTERMINISME ---")
for i in range(3):
    print(f"Run {i}: {run_test('Appliquer procédure')}")

# Test Vérificateur (Circuit incorrect - on modifie temporairement le circuit)
# ...
