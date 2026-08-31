import sqlite3
import json
import os

# Dossier contenant les backups SQLite
BACKUP_DIR = '/root/.gemini/tmp/ssh/local_circuits/sauvegardes-tour/backups/'
REGISTRY_FILE = '/root/.gemini/tmp/ssh/local_tour/registry.json'

def extract_circuits():
    circuits = {}
    
    # Trouver le dernier backup SQLite
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.sqlite')]
    if not files:
        print("Aucun fichier SQLite trouvé.")
        return
    
    latest_file = max([os.path.join(BACKUP_DIR, f) for f in files], key=os.path.getmtime)
    print(f"Extraction depuis : {latest_file}")
    
    conn = sqlite3.connect(latest_file)
    cursor = conn.cursor()
    
    # Lister les tables pour trouver le nom correct
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables trouvées : {tables}")
    
    # Chercher une table qui ressemble à 'circuit'
    circuit_table = next((t for t in tables if 'circuit' in t.lower()), None)
    
    if not circuit_table:
        print("Aucune table de circuit trouvée.")
        return
        
    print(f"Table de circuits identifiée : {circuit_table}")
    
    # Extraction des circuits
    cursor.execute(f"SELECT name, active FROM {circuit_table} WHERE active = 1")

    # Mise à jour du registre local
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r') as f:
            current_registry = json.load(f)
    else:
        current_registry = {}
        
    current_registry.update(circuits)
    
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(current_registry, f, indent=2)
    
    print(f"Importé {len(circuits)} circuits dans {REGISTRY_FILE}")
    conn.close()

if __name__ == "__main__":
    extract_circuits()
