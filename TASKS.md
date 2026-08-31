# Tâches et Problèmes à résoudre

 - [x] **Développer import_circuits.py** : Extraire les circuits réels (`webmcp.circuit`) depuis les fichiers SQLite de sauvegarde (`/root/.gemini/tmp/ssh/local_circuits/sauvegardes-tour/backups/*.sqlite`).
 - [x] **Adapter les circuits** : Convertir la logique Odoo extraite pour qu'elle fonctionne avec le routeur déterministe local (Python standard).
 - [x] **Vérifier l'intégration** : Mettre à jour `registry.json` avec les circuits importés.
 - [x] **Rendre le routeur MCP-compatible** : Créer un manifeste `mcp.json` pour que le routeur déterministe puisse être enregistré par `opencode`.
 - [x] **Réconcilier le diagnostic MCP** : Enquêter sur la configuration pour comprendre pourquoi les anciennes traces existent si Opencode n'est pas connecté.
