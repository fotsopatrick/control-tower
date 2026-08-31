import json
import urllib.request
import sys

def select_strategy(prompt):
    # Appel modèle Qwen (via local Ollama)
    data = json.dumps({"model": "qwen2.5:7b", "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request("http://20.97.179.141:11434/api/generate", data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        return res["response"].strip()

if __name__ == "__main__":
    prompt = sys.stdin.read()
    print(select_strategy(prompt))
