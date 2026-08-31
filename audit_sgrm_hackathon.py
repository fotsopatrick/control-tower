#!/usr/bin/env python3
"""
AUDIT INDEPENDANT - Projet SGRM (All Things Agentic Hackathon)

Ce script ne fait CONFIANCE A RIEN de ce que l'agent a déclaré.
Il vérifie sur le disque, ligne par ligne, si les affirmations du
"RAPPORT FINAL DE MISSION" sont vraies ou fausses.

Usage :
    python3 audit_sgrm_hackathon.py [chemin_du_projet]

Par défaut, cherche dans /home/orel/SGRM_PROJECT/
Affiche un verdict PASS/FAIL par affirmation, et un verdict global.
Ne modifie AUCUN fichier.
"""

import sys
import os
import re
import json
from pathlib import Path

# ----------------------------------------------------------------------
# Résultats collectés au fil de l'audit
# ----------------------------------------------------------------------
RESULTS = []  # liste de (nom_check, PASS/FAIL/WARN, détail)


def check(name, passed, detail, warn=False):
    status = "WARN" if warn else ("PASS" if passed else "FAIL")
    RESULTS.append((name, status, detail))
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ "}[status]
    print(f"{icon} [{status}] {name}")
    if detail:
        print(f"       -> {detail}")


def read_text_safe(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return None


def find_files(root, patterns):
    """Retourne tous les fichiers du repo dont le nom matche un des patterns (glob)."""
    found = []
    for pattern in patterns:
        found.extend(root.rglob(pattern))
    # ignore les dossiers lourds inutiles
    return [f for f in found if not any(
        part in (".git", "node_modules", "__pycache__", "venv", ".venv")
        for part in f.parts
    )]


def main():
    project_root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/orel/SGRM_PROJECT")

    print("=" * 70)
    print(f"AUDIT INDEPENDANT — {project_root}")
    print("=" * 70)

    if not project_root.exists():
        print(f"❌ Le dossier {project_root} n'existe pas. Impossible d'auditer.")
        sys.exit(2)

    # --------------------------------------------------------------
    # 1. AFFIRMATION : "Intégration de Gemini 3.5"
    #    -> il faut trouver un VRAI appel API, pas juste le mot "gemini"
    #       quelque part dans un commentaire ou un nom de variable.
    # --------------------------------------------------------------
    py_files = find_files(project_root, ["*.py"])
    gemini_call_pattern = re.compile(
        r"(genai\.Client|GenerativeModel|generate_content|"
        r"vertexai\.init|from google import genai|"
        r"google\.genai)", re.IGNORECASE
    )
    gemini_model_string = re.compile(r"gemini-3\.5", re.IGNORECASE)

    files_with_call = []
    files_with_model_string = []
    for f in py_files:
        content = read_text_safe(f)
        if not content:
            continue
        if gemini_call_pattern.search(content):
            files_with_call.append(str(f.relative_to(project_root)))
        # L'auditeur ne se valide plus lui-meme : sa propre expression de
        # recherche contient « gemini-3.5 », et elle passait pour une preuve.
        if f.name == "audit_sgrm_hackathon.py":
            continue
        if gemini_model_string.search(content):
            files_with_model_string.append(str(f.relative_to(project_root)))

    check(
        "Appel réel à l'API Gemini (pas juste le mot 'gemini')",
        len(files_with_call) > 0,
        f"Fichiers avec un appel SDK détecté : {files_with_call}" if files_with_call
        else "Aucun fichier .py ne contient un vrai appel genai/GenerativeModel/generate_content",
    )
    # EXIGENCE OBLIGATOIRE du reglement All Things Agentic : Gemini 3.5 ou
    # plus recent. Le controle vise le ROUTEUR, pas le depot entier : un nom
    # de modele cite dans un README ne fait tourner aucun service.
    routeur = project_root / "gcp_router" / "main.py"
    contenu_routeur = read_text_safe(routeur) or ""
    premier = re.search(r'"(gemini-[^",]+)', contenu_routeur)
    premier_modele = premier.group(1) if premier else "(aucun)"
    conforme = premier_modele.startswith("gemini-3.")
    check(
        "Le routeur appelle Gemini 3.5 ou plus recent (exigence obligatoire)",
        conforme,
        f"gcp_router/main.py essaie d'abord : {premier_modele}" if conforme
        else f"NON CONFORME : le routeur essaie d'abord {premier_modele}, "
             f"le reglement exige gemini-3.5 minimum",
    )
    check(
        "Le modèle 'gemini-3.5' est référencé ailleurs que dans l'auditeur",
        len(files_with_model_string) > 0,
        f"Trouvé dans : {files_with_model_string}" if files_with_model_string
        else "Le string 'gemini-3.5' n'apparaît nulle part hors de l'auditeur",
        warn=not files_with_model_string,
    )

    # --------------------------------------------------------------
    # 2. AFFIRMATION : "Google GenAI SDK"
    #    -> doit être une dépendance déclarée, pas juste importée
    #       en espérant qu'elle soit installée par hasard.
    # --------------------------------------------------------------
    dep_files = find_files(project_root, ["requirements*.txt", "pyproject.toml", "Pipfile"])
    sdk_declared = False
    dep_detail = []
    for f in dep_files:
        content = read_text_safe(f) or ""
        if re.search(r"google-genai|google-cloud-aiplatform|vertexai", content, re.IGNORECASE):
            sdk_declared = True
            dep_detail.append(str(f.relative_to(project_root)))

    check(
        "Le SDK Google GenAI est déclaré comme dépendance officielle",
        sdk_declared,
        f"Déclaré dans : {dep_detail}" if dep_detail
        else "Aucun fichier de dépendances (requirements.txt / pyproject.toml) ne mentionne google-genai ou vertexai — le code peut planter sur une machine propre",
    )

    # --------------------------------------------------------------
    # 3. AFFIRMATION : "Cloud Run (via Dockerfile)"
    # --------------------------------------------------------------
    dockerfiles = find_files(project_root, ["Dockerfile", "Dockerfile.*"])
    dockerfile_ok = False
    dockerfile_detail = "Aucun Dockerfile trouvé"
    if dockerfiles:
        content = read_text_safe(dockerfiles[0]) or ""
        has_expose_or_port = bool(re.search(r"EXPOSE|PORT", content, re.IGNORECASE))
        has_cmd = bool(re.search(r"^(CMD|ENTRYPOINT)", content, re.MULTILINE))
        dockerfile_ok = has_expose_or_port and has_cmd
        dockerfile_detail = (
            f"{dockerfiles[0].relative_to(project_root)} — "
            f"EXPOSE/PORT présent: {has_expose_or_port}, CMD/ENTRYPOINT présent: {has_cmd}"
        )
    check(
        "Dockerfile présent ET compatible Cloud Run (PORT + CMD)",
        dockerfile_ok,
        dockerfile_detail,
    )

    # --------------------------------------------------------------
    # 4. AFFIRMATION : "vérifié par l'oracle indépendant"
    #    -> il doit exister une trace de test réellement exécuté
    #       (rapport, logs, fichier de résultats), pas juste une
    #       déclaration verbale.
    # --------------------------------------------------------------
    test_files = find_files(project_root, ["test_*.py", "*_test.py"])
    result_artifacts = find_files(project_root, [
        "*report*.json", "*results*.json", "*report*.txt",
        "*.log", "pytest_report*", "*ORACLE*"
    ])
    check(
        "Des fichiers de test existent réellement dans le repo",
        len(test_files) > 0,
        f"{len(test_files)} fichier(s) de test trouvé(s) : {[str(f.relative_to(project_root)) for f in test_files]}"
        if test_files else "Aucun fichier test_*.py ou *_test.py trouvé — 'vérifié par l'oracle' n'a pas de test associé visible",
    )
    check(
        "Un artefact de résultat d'exécution (rapport/log) existe, daté",
        len(result_artifacts) > 0,
        f"Trouvé : {[str(f.relative_to(project_root)) for f in result_artifacts]}" if result_artifacts
        else "Aucune preuve écrite qu'un test a réellement tourné (pas de log, pas de rapport JSON) — l'affirmation 'vérifié' repose uniquement sur la parole de l'agent",
        warn=not result_artifacts,
    )

    # --------------------------------------------------------------
    # 5. AFFIRMATION : "Documentation complète dans docs/"
    # --------------------------------------------------------------
    docs_dir = project_root / "docs"
    readme_candidates = find_files(project_root, ["README*.md", "README*.txt"])
    demo_script_candidates = find_files(project_root, ["*demo*"])
    arch_diagram_candidates = find_files(project_root, ["*architecture*", "*diagram*"])

    check(
        "README présent",
        len(readme_candidates) > 0,
        f"{[str(f.relative_to(project_root)) for f in readme_candidates]}" if readme_candidates else "Aucun README trouvé",
    )
    if readme_candidates:
        readme_content = read_text_safe(readme_candidates[0]) or ""
        has_spinup = bool(re.search(r"spin.?up|installation|getting started|setup", readme_content, re.IGNORECASE))
        check(
            "Le README contient des instructions de spin-up (exigence explicite du règlement)",
            has_spinup,
            "Section setup/installation détectée" if has_spinup else "Aucune section d'installation détectée dans le README",
        )
    check(
        "Un script/plan de démo existe",
        len(demo_script_candidates) > 0,
        f"{[str(f.relative_to(project_root)) for f in demo_script_candidates]}" if demo_script_candidates else "Rien trouvé",
    )
    check(
        "Un diagramme d'architecture existe (fichier, pas juste 'textuel' dans le rapport)",
        len(arch_diagram_candidates) > 0,
        f"{[str(f.relative_to(project_root)) for f in arch_diagram_candidates]}" if arch_diagram_candidates else "Aucun fichier ne contient 'architecture' ou 'diagram' dans son nom — vérifier si le diagramme existe vraiment comme fichier ou seulement dans le rapport de l'agent",
    )

    # --------------------------------------------------------------
    # VERDICT GLOBAL
    # --------------------------------------------------------------
    print("\n" + "=" * 70)
    n_fail = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    n_warn = sum(1 for _, s, _ in RESULTS if s == "WARN")
    n_pass = sum(1 for _, s, _ in RESULTS if s == "PASS")
    print(f"RÉSUMÉ : {n_pass} PASS / {n_warn} WARN / {n_fail} FAIL sur {len(RESULTS)} vérifications")

    if n_fail == 0 and n_warn == 0:
        verdict = "CONFORME — les affirmations du rapport sont corroborées par le disque."
    elif n_fail == 0:
        verdict = "PARTIELLEMENT CONFORME — pas d'échec net, mais des zones d'ombre (WARN) à vérifier avant soumission."
    else:
        verdict = "NON CONFORME — au moins une affirmation du rapport n'est PAS corroborée par le contenu réel du dépôt."

    print(f"VERDICT : {verdict}")
    print("=" * 70)

    # code de sortie utile pour un pipeline CI ou un autre agent
    sys.exit(1 if n_fail > 0 else 0)


if __name__ == "__main__":
    main()
