# Final Experimental Validation — La Tour

## 1. Research Question
Peut-on remplacer un sélecteur déterministe par un petit modèle (Qwen 2.5 7B) pour piloter des circuits déterministes dans La Tour ?

## 2. Hypothesis
Un petit modèle peut apprendre à sélectionner la bonne stratégie de raisonnement (circuit), améliorant la flexibilité tout en garantissant l'exactitude via un oracle indépendant.

## 3. Architecture
- **Sélecteur** : LLM (Qwen 2.5 7B) + Bridge
- **Circuit** : Python (Déterministe)
- **Oracle** : Indépendant (Logique mathématique directe)

## 4. Experimental Method
Audit de code, tests unitaires, induction d'erreurs (failure modes), mesures de latence.

## 5. Reference Experiment (Input: 17)
- Expected: 712
- Actual: 712
- Status: PASS

## 6. LLM Selector Results
- Stratégie correcte sur 100% des cas testés (Nominal).

## 7. Deterministic Circuit Results
- 100% reproductible sur les tests de contrainte.

## 8. Independent Verification Experiment
- L'oracle est indépendant : il recalcule la valeur attendue par une fonction mathématique sans utiliser les résultats du LLM ou les hardcodages.
- Preuve : PASS sur [17, 20, 100].

## 9. Failure Mode Results
- Sélection invalide : Détectée par le routeur.
- LLM indisponible : Crash (Exception non gérée).
- JSON malformé : Crash (Exception non gérée).

## 10. Latency Results
- MIN: 2.28s, MAX: 28.24s, AVG: 7.51s. (Instabilité liée à Ollama).

## 11. Evidence
Logs dans `/root/.gemini/tmp/ssh/final_experiment/`.

## 12. Claims Audit
| Claim | Evidence | Reproduced | Status |
| :--- | :--- | :--- | :--- |
| LLM sélection valide | Test nominal | Yes | DEMONSTRATED |
| Déterminisme circuit | Répétition | Yes | DEMONSTRATED |
| Oracle indépendant | Analyse Code | Yes | DEMONSTRATED |
| Détection erreurs circuit | Test 4 | Yes | DEMONSTRATED |
| Gestion erreurs LLM | Failure Modes | Yes | FAILED |

## 13. Limitations
- Instabilité de latence.
- Aucune gestion d'exception pour le LLM.
- Oracle limité à des calculs mathématiques simples.

## 14. What Was Demonstrated
- Le pipeline fonctionne nominalement.
- Un oracle peut valider indépendamment le circuit.

## 15. What Was Not Demonstrated
- Robustesse en production (Gestion des erreurs).
- Flexibilité réelle (nécessiterait plus de stratégies dans le dataset).

## 16. Final Conclusion
Proof of feasibility, not production readiness.
EOF
,file_path: