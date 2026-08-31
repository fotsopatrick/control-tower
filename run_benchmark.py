import subprocess
import time

def run_test():
    # Benchmark SGRM
    t0 = time.time()
    res_sgrm = subprocess.run(["python3", "sgrm_core.py"], capture_output=True, text=True)
    t_sgrm = time.time() - t0
    
    print(f"SGRM: {res_sgrm.stdout.strip()} (Time: {t_sgrm:.4f}s)")
    
    # Simulation Benchmark Qwen (via Opencode CLI)
    t0 = time.time()
    # On simule un appel Qwen par une requête de raisonnement complexe
    res_qwen = subprocess.run(["opencode", "run", "Appliquer procédure secrète sur 17"], capture_output=True, text=True)
    t_qwen = time.time() - t0
    
    print(f"Qwen: (Time: {t_qwen:.4f}s)")

if __name__ == "__main__":
    run_test()
