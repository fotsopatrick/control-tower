# EXPERIMENTAL VALIDATION REPORT

## 1. Hypothèse
Peut-on remplacer un sélecteur déterministe par un petit modèle (Qwen 2.5 7B) pour piloter des circuits déterministes dans La Tour ?

## 2. Architecture testée
- **Sélecteur** : Qwen 2.5 7B (API Ollama)
- **Circuit** : Python (`apply_procedure.py`)
- **Vérificateur** : Python (asserts)

## 3. Reference test
- Input: [op_q9, op_k7, op_m2] sur 17
- Expected: 712
- Result: 712 (PASS)
- Temps moyen : ~2.3s

## 4. Experimental corpus
- Nominal : Validé
- Déterminisme : Validé (3/3 runs identiques)

## 5. Failure modes
- **Sélection invalide** : Le système échoue proprement ("Échec sélection stratégie").
- **LLM Indisponible** : Le système lève une exception non gérée (risque de blocage).
- **Sortie malformée** : JSON.loads() lève une exception (risque de blocage).

## 6. Demonstrated properties
- **P1 (Sélecteur LLM valide)** : [DÉMONTRÉE]
- **P4 (Déterminisme circuit)** : [DÉMONTRÉE]

## 7. Remaining risks
- Gestion des erreurs LLM (timeout, JSON malformé) : [À DÉVELOPPER]
- Persistance de la mémoire du modèle : [NON DÉMONTRÉE]

## 8. Final conclusion
L'architecture est viable pour un remplacement partiel. Le sélecteur LLM apporte de la flexibilité, tandis que le circuit déterministe garantit l'exactitude du calcul final.
EOF
,file_path: