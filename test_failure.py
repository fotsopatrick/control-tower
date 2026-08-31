import subprocess
# Inject invalid strategy
res = subprocess.run(["python3", "-c", "print('invalid_strategy')"], capture_output=True, text=True)
# Simulation du routeur rejetant
strategy = res.stdout.strip()
if strategy not in ["séquentiel", "déduction"]:
    print("Failure Mode: INVALID_STRATEGY")
