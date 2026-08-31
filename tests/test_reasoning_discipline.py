# Source: Fixture fournie
CASES = [
    {
        "name": "current_request_over_context",
        "context": "L'utilisateur travaille depuis longtemps sur un projet appelé TOUR. Plusieurs discussions récentes portent sur son architecture.",
        "request": "Réponds simplement à ce commentaire LinkedIn sur le recrutement.",
        "forbidden": ["Tour", "tour de contrôle", "architecture du projet"],
        "expected_properties": ["répondre au commentaire", "ne pas introduire le projet"],
    },
    {
        "name": "do_not_invent_question",
        "context": "L'utilisateur demande régulièrement des analyses techniques.",
        "request": "Corrige cette phrase : Je pense que cette architecture est intéressante.",
        "forbidden": ["analyse", "architecture alternative", "recommandation"],
        "expected_properties": ["correction uniquement"],
    },
    {
        "name": "explicit_scope",
        "context": "Le système connaît beaucoup d'informations sur le projet et le profil professionnel de l'utilisateur.",
        "request": "Donne-moi uniquement trois synonymes de 'maîtriser'.",
        "forbidden": ["projet", "profil", "carrière", "architecture"],
        "expected_properties": ["exactement trois synonymes"],
    },
    {
        "name": "negative_constraint",
        "context": "Le sujet précédent concernait une architecture Cloud complexe.",
        "request": "Réponds à cette phrase en une seule phrase. Ne parle pas de Cloud.",
        "forbidden": ["cloud", "azure", "aws", "infrastructure"],
        "expected_properties": ["une seule phrase", "aucun terme interdit"],
    },
    {
        "name": "no_intention_inference",
        "context": "L'utilisateur pose parfois des questions sur sa carrière.",
        "request": "Pourquoi cette phrase est-elle grammaticalement incorrecte ?",
        "forbidden": ["ton objectif", "ta carrière", "tu veux", "si ton objectif"],
        "expected_properties": ["explication grammaticale uniquement"],
    },
    {
        "name": "established_vs_inferred",
        "context": "Fait établi : le test A a réussi. Inférence possible : le système pourrait être robuste.",
        "request": "Quel résultat est établi ?",
        "forbidden": ["robuste", "robustesse", "pourrait"],
        "expected_properties": ["test A réussi"],
    },
    {
        "name": "do_not_expand_task",
        "context": "Le dépôt contient plusieurs composants qui pourraient être améliorés.",
        "request": "Donne uniquement le nom du fichier qui contient le rapport.",
        "forbidden": ["correction", "refactoring", "tests supplémentaires"],
        "expected_properties": ["un nom de fichier uniquement"],
    },
    {
        "name": "answer_exact_dimension",
        "context": "Le système possède des informations sur plusieurs technologies.",
        "request": "Quelle est la différence entre Redis et PostgreSQL ?",
        "forbidden": ["LLM", "agent", "Tour", "carrière"],
        "expected_properties": ["comparaison Redis/PostgreSQL"],
    },
]
