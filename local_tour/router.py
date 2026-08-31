import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import guardrails
import os

class TourRouter(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length))
        
        # Charger le registre
        with open('registry.json', 'r') as f:
            registry = json.load(f)
            
        skill_name = body['params']['name']
        
        # 1. Vérification des Garde-fous (Guardrails)
        if not guardrails.is_allowed(skill_name):
            self.send_error(403, "Garde-fou activé : accès refusé.")
            return

        # 2. Exécution déterministe
        if skill_name in registry:
            script_path = registry[skill_name]['path']
            if os.path.exists(script_path):
                result = subprocess.run(['python3', script_path], capture_output=True, text=True)
                output = result.stdout
            else:
                output = f"Circuit non trouvé: {script_path}"
        else:
            output = "Compétence inconnue"
        
        # 3. Réponse JSON-RPC
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"jsonrpc": "2.0", "result": output}).encode())

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8080), TourRouter)
    print("Serveur local déterministe démarré sur port 8080...")
    server.serve_forever()
