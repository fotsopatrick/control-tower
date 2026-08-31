import time, subprocess
import statistics

latencies = []
for _ in range(5):
    t0 = time.time()
    # Appel du sélecteur réel
    subprocess.run(["python3", "/root/.gemini/tmp/ssh/local_tour/sgrm_selector.py"], capture_output=True, text=True)
    latencies.append(time.time() - t0)

print(f"MIN: {min(latencies):.4f}s, MAX: {max(latencies):.4f}s, AVG: {statistics.mean(latencies):.4f}s")
