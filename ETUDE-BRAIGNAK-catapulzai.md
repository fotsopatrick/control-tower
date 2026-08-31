# Étude — CatapulZ AI, et ce qu'elle nous prend

> **Traité avec les specs de Braignak (« L'observateur », compétence native
> `predateur`), par Claude, le 31/08/2026 à 14:45 — heure de Paris.**
> Compétence **usurpateur** (`specs/COMPETENCE-USURPATEUR.md`, posée le
> 09/08/2026). Braignak n'a pas été prévenu et rien ne lui a été envoyé.
> S'il traite lui-même plus tard, **c'est lui qui a le dernier mot**.
>
> **BROUILLON.** Braignak ne publie rien et ne modifie rien. Aucun fichier du
> rendu n'a été touché par cette étude.

---

## 0. Le mot que je n'ai pas pu établir : « décathlon »

Patrick a dit « notre rendu pour le décathlon ». Je n'ai **aucune trace** de ce
mot. Braignak interdit de dire « ça n'existe pas ». Je dis donc où j'ai cherché :

| Lieu fouillé | Date de la lecture | Résultat |
|---|---|---|
| La carte vivante de la tour, 483 éléments, 9 zones | 31/08/2026 14:37 | rien |
| La tour : `~/tour`, `~/chantiers-tour`, `~/outils` | 31/08/2026 14:42 | rien de réel |
| Le poste nomi : tout `/home/orel` (md, txt, json, sh, py) | 31/08/2026 14:42 | rien de réel |
| La page catapulzai, texte entier | 31/08/2026 14:41 | le mot est absent |

Les seuls résultats étaient des **listes de mots de passe** (`rockyou.txt`) et
des **fichiers internes de Chrome**. C'est du bruit, pas une trace.

**Hypothèse 1 (retenue)** — « décathlon » est le mot de Patrick pour le
**hackathon « All Things Agentic »**, piste *The Fortified Enterprise Fleet*.
C'est le seul rendu qui existe (`livraison-hackathon/`) et il a été modifié
**le jour même, quelques minutes avant la demande**.

**Hypothèse 2** — c'est un autre concours, dont je n'ai encore aucune trace.

**L'observation qui tranche** : une phrase de Patrick. Si c'est l'hypothèse 2,
toute la partie 4 de cette étude est à refaire sur la bonne cible.

Toute la suite est écrite **sous l'hypothèse 1**.

---

## 1. La cible

**CatapulZ AI — « Master Agentic AI »**, `catapulzai.eu`, fondée par Wilfried.
Formation en ligne, 97 € par mois, résiliable après 6 mois.
Lue en entier le 31/08/2026 à 14:41.

**La licence, relevée AVANT toute chose** (règle de Braignak) :
« © 2026 CatapulZ AI — Tous droits réservés ». C'est du **tout droits
réservés**. Conséquence directe et non négociable : **on ne reprend aucun
texte, aucune image, aucune formulation**. On n'a le droit d'observer que la
*façon de faire*. Une manière de présenter ne se possède pas ; une phrase, si.
Rien dans cette étude ne recopie leur page.

**Ce que la cible vend** : six blocs de compétences pour construire des agents
IA — piloter Claude, coder sans coder, orchestrer avec Dust et N8N,
architectures MCP et RAG multi-agents, agents vocaux, et OpenClaw.

---

## 2. Ce qu'elle fait que notre rendu ne fait pas

C'est le cœur du métier de prédateur. Cinq écarts, tous vérifiés sur les deux
documents.

### Écart 1 — Elle chiffre une **conséquence**. Nous chiffrons un **mécanisme**.

Notre rendu prouve : `model_calls = 0`, 27 millisecondes, audit 10 sur 10.
Ce sont de vraies mesures, et elles sont solides.
Mais un juge lit `model_calls = 0` et doit **traduire tout seul**.

Eux écrivent ce que le chiffre *change* : le temps de fabrication d'une
proposition commerciale passe de deux jours à deux heures.

Le nôtre s'arrête une case trop tôt. Il ne dit jamais **ce que zéro appel
modèle fait gagner** : de l'argent, du délai, ou une garantie.

### Écart 2 — Elle raconte une **scène**. Nous listons des **noms d'outils**.

Notre démonstration montre `read_carte`, `create_task`, `drop_database`.
Ce sont des noms de fonctions. Personne ne se les représente.

Eux montrent un directeur d'hôtel au bord de l'épuisement, ses équipes qui le
harcèlent toute la journée. On voit la scène en une phrase.

`drop_database` refusé, c'est excellent — mais **personne ne sait de quelle
base il s'agit**, ni ce qui se serait passé si la porte avait cédé.

### Écart 3 — Elle donne à chaque agent **un rôle en une ligne**. Nous donnons un schéma.

Chez eux : un agent qui cherche les profils, un qui prépare l'entretien, un qui
note, un qui rédige. Une ligne chacun, on comprend l'équipe en dix secondes.

Notre architecture est un diagramme plus une table de noms techniques. C'est
juste, mais ça se lit lentement — et un jury lit vite.

### Écart 4 — Elle affiche un **engagement en cas d'échec**. Nous n'en affichons aucun.

Eux : remboursement sous trois jours, sans justification.
C'est une promesse **tenable et vérifiable**.

Notre Control Tower **refuse** des choses — c'est sa plus belle qualité. Mais
le rendu ne dit nulle part **ce qu'il promet quand il refuse** : que se
passe-t-il pour l'utilisateur ? Il attend ? On l'escalade ? Ça tombe ?
Un refus sans promesse de suite ressemble à une panne.

### Écart 5 — Elle répond aux **objections** de front. Nous répondons aux nôtres.

Leur page attaque la seule question qui tue : en quoi c'est différent d'une
formation ChatGPT ordinaire.

Notre rendu a des « Mandatory disclosures » et une « Honest limitation ».
C'est **plus honnête qu'eux** et il faut le garder. Mais ça répond à *nos*
scrupules, pas à l'objection du juge. Or l'objection du juge existe, elle est
évidente, et elle n'est traitée nulle part :

> « Votre routeur déterministe, c'est un `if` dans un registre. Où est le
> travail ? »

Ne pas y répondre, c'est laisser le juge y répondre à notre place.

---

## 3. Ce que NOUS avons et qu'elle n'a pas — à ne surtout pas perdre

Le prédateur ne rapporte pas que des manques.

Leurs chiffres sont des **témoignages**. « −85 % », signé par un prénom et une
initiale. Rien ne les vérifie. C'est invérifiable par construction.

Nous avons `audit_sgrm_hackathon.py` : un programme qui **relit le rendu et
fait échouer la construction si une affirmation n'est pas confirmée par les
fichiers**. Il a été écrit précisément parce qu'une version précédente du
projet annonçait une intégration Gemini que le code ne faisait pas.

C'est exactement la façon de penser de la tour : **une porte qui refuse fait
son travail**. C'est notre avantage réel sur eux, et il n'est pas mis en avant.

---

## 4. La capacité qui manque — une seule

> **Le convertisseur de preuve.**
> Pour chaque fait technique mesuré, écrire à côté, sur la même ligne, la
> conséquence lisible — et la faire vérifier par le même auditeur.

Ni du maquillage, ni du marketing : une **colonne de plus**, soumise au même
contrôle que le reste. Si la conséquence n'est pas calculable depuis une mesure
réelle, l'audit la refuse. On garde donc notre honnêteté **et** on devient
lisible.

### Le prototype proposé (brouillon, non appliqué)

**a) Un tableau à trois colonnes, en haut du README, avant tout le reste :**

| Ce qui est mesuré | La preuve sur disque | Ce que ça change |
|---|---|---|
| 5 requêtes sur 6 traitées sans modèle | `/metrics`, `model_calls = 0` | 5 requêtes sur 6 ne coûtent rien et ne peuvent pas halluciner |
| 27 ms sur une capacité connue | `preuve-execution-cloud.txt` | réponse ~100 fois plus rapide qu'un aller-retour modèle |
| `drop_database` refusé sans modèle | `demo_flight.sh` étape 4 | la destruction ne dépend pas de l'humeur d'un modèle |
| 10 contrôles sur 10 au vert | `audit-conformite.txt` | aucune phrase du rendu n'est invérifiée |

**b) Une scène nommée pour remplacer les noms de fonctions.**
Garder les mêmes appels, mais les habiller : `drop_database` devient
« un agent reçoit l'ordre d'effacer la base clients ». Même code, même preuve,
scène visible.

**c) Une porte-avec-promesse.**
Chaque refus dit ce qui se passe après : qui est prévenu, sous quel délai, et
comment on le débloque. Un refus qui indique la suite est une garantie ; un
refus muet est une panne.

**d) Trois objections, trois réponses courtes**, dont obligatoirement
« c'est juste un `if` » — à laquelle la réponse est déjà dans le dépôt : le
registre est déclaré, mesuré et audité, et le repli modèle est réel et compté.

---

## 5. Les trois niveaux (règle du colonel, 04/08)

- **Le geste (tactique)** — ajouter la colonne « ce que ça change » et les
  trois objections. Une heure de travail. Aucun code touché.
- **La manœuvre (opérationnel)** — étendre `audit_sgrm_hackathon.py` pour
  qu'il contrôle aussi les conséquences : une conséquence sans mesure derrière
  fait **échouer** la construction, comme une affirmation sans preuve.
- **La raison (stratégique)** — notre thèse n'est pas « nous appelons moins le
  modèle ». C'est : **le déterminisme est ce qui rend une promesse tenable**.
  CatapulZ promet et demande qu'on la croie. Nous pouvons promettre **et
  prouver**. C'est ça, notre place — et le rendu ne la revendique pas encore.

---

## 6. Confiance

**0,75.**

Ce qui la tient : la page cible a été lue en entier, pas de mémoire ; les deux
documents du rendu ont été lus en entier ; les cinq écarts sont vérifiables
ligne par ligne dans les deux textes.

Ce qui la retient : le mot « décathlon » n'est pas établi (partie 0), et **je
n'ai pas le règlement du concours**. Sans la grille de notation, je compare
notre rendu à une page de vente — pas à ce sur quoi il sera réellement jugé.
Avec le règlement, la confiance monterait à 0,9.

---

## 7. Les trois lignes

- **Fait** — Cible lue en entier, licence relevée (tous droits réservés, on ne
  copie rien). Rendu lu en entier. Cinq écarts établis, un avantage à nous
  identifié, une capacité manquante déduite, un prototype écrit. Rien n'a été
  publié ni modifié.
- **Suivant** — Appliquer le point (a) : le tableau à trois colonnes en tête du
  README du rendu. C'est le geste le plus court avec le plus d'effet, et il ne
  demande personne.
- **Bloqué par** — **Patrick**, sur deux points : confirmer ce qu'est le
  « décathlon », et fournir le **règlement / la grille de notation** du
  concours. Sans elle, j'améliore à l'aveugle.
