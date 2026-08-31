# Étude v2 — notre rendu face au VRAI règlement

> **Traité avec les specs de Braignak (« L'observateur », compétence native
> `predateur`), par Claude, le 31/08/2026 à 15h10 — heure de Paris.**
> Compétence **usurpateur** (`specs/COMPETENCE-USURPATEUR.md`, 09/08/2026).
> Braignak n'a pas été prévenu et rien ne lui a été envoyé. S'il traite
> lui-même plus tard, **c'est lui qui a le dernier mot**.
>
> **BROUILLON. Aucun fichier du rendu n'a été modifié.**
>
> Cette étude **remplace** `ETUDE-BRAIGNAK-catapulzai.md`, écrite une heure
> plus tôt **sans le règlement**. Sa partie 0 disait : « je n'ai pas le
> règlement, donc je compare à une page de vente, pas à ce sur quoi on sera
> jugé ». Le règlement est maintenant là. La comparaison change du tout au tout.

---

## 0. Ce qui est enfin établi — et d'où ça vient

| Fait | Source, lue en entier | Quand |
|---|---|---|
| Concours = **All Things Agentic Hackathon**, sur Devpost | courriel `support@devpost.com`, « You're in! » | reçu 29/08 |
| Tu es **inscrit** et tu as **commencé** un dépôt | courriel « Submission to All Things Agentic Hackathon started » | 29/08 |
| Piste choisie = **The Fortified Enterprise Fleet** | le README du rendu | — |
| **DATE LIMITE : 1er septembre 2026 à 02h00** | page publique du concours | lue le 31/08 à 15h02 |
| Prix de notre piste : **20 000 dollars** | même page | — |

**Il reste environ ONZE HEURES.** Tout ce qui suit est classé par urgence,
pas par élégance.

Le mot « décathlon » de ta demande = ce hackathon. **Hypothèse 1 de l'étude v1
confirmée.** L'hypothèse 2 est écartée.

---

## 1. 🔴 LE DANGER : on peut être écarté avant même d'être noté

Le règlement pose trois choses **obligatoires pour toutes les catégories** :

1. **Gemini 3.5 ou plus récent** (par l'API Gemini ou Vertex AI)
2. au moins un cadre d'agents Google — ADK, GenAI SDK, Antigravity SDK, Genkit
3. au moins un service Google Cloud — Cloud Run, Cloud SQL, Firestore…

Les points 2 et 3 sont tenus : nous utilisons le **GenAI SDK** (la bibliothèque
`google-genai`) et **Cloud Run**. ✅ ✅

**Le point 1 ne l'est pas.**

| Où j'ai regardé | Ce que j'ai trouvé |
|---|---|
| `gcp_router/main.py`, ligne 32 | `gemini-2.5-flash, gemini-flash-latest, gemini-2.0-flash, gemini-1.5-flash` |
| `livraison-hackathon/preuve-execution-cloud.txt` | **8 fois** `"model":"vertex/gemini-2.5-flash"` |
| `livraison-hackathon/preuve-deux-modeles.txt` | `A decision=NO_MATCH model=vertex/gemini-2.5-flash` |
| le README du rendu | « the router tries `gemini-2.5-flash` first » |

Le service **réellement déployé** a répondu en **Gemini 2.5**. Pas 3.5.
Ce n'est pas une note en moins : c'est une **condition d'entrée**.

### Et le vert qui ment

`audit_sgrm_hackathon.py` affiche : ✅ « Le modèle 'gemini-3.5' est
explicitement référencé quelque part ». Il dit vrai — et il ne veut rien dire.

Le contrôle cherche le texte `gemini-3.5` **n'importe où dans le dépôt**
(ligne 79). Il le trouve… **dans sa propre ligne 79**, là où le motif de
recherche est écrit. Le rapport le montre noir sur blanc :

> `-> Trouvé dans : ['audit_sgrm_hackathon.py']`

**L'auditeur se valide lui-même.** C'est exactement le genre de dérive que ce
programme a été écrit pour attraper — il vient de se la faire à lui-même. Un
contrôle qui n'a jamais pu refuser ne garde rien.

**Le geste** : le contrôle doit chercher **dans le code du routeur**, pas dans
le dépôt entier, et **s'exclure lui-même**. Il doit passer au **rouge**
maintenant, avant qu'on corrige le modèle. Un contrôle qui ne rougit pas quand
c'est faux n'est pas un contrôle.

### ✅ VÉRIFIÉ — et la voie est libre

Testé en direct le 31/08/2026 à 15h05 sur ton projet `control-tower-hackathon`,
via `gcloud` connecté au compte `fotsoorel95@gmail.com` :

| Modèle demandé | Réponse de Google |
|---|---|
| **`gemini-3.5-flash`** | ✅ **répond** — il a renvoyé « OK » |
| `gemini-3.5-pro` | ❌ n'existe pas sur ce projet |
| `gemini-3-flash` | ❌ n'existe pas sur ce projet |
| `gemini-3-pro` | ❌ n'existe pas sur ce projet |

**Le modèle conforme est disponible et il fonctionne.** La correction est donc
sans risque : mettre **`gemini-3.5-flash` en tête** de la liste ligne 32 de
`gcp_router/main.py`, garder les autres derrière comme secours, redéployer,
puis refaire tourner les preuves.

C'est **une ligne**. Elle sépare un dossier hors-concours d'un dossier
recevable.

---

## 2. Les critères de notation — et où nous sommes

Le concours note sur trois blocs. Les voici, et notre position honnête.

### 🟠 40 % — « Innovation & Operational Utility »

> *Combien de friction réelle l'agent enlève-t-il **tout seul** ? On récompense
> l'**action autonome à forte valeur**, pas la simple conversation — des agents
> qui décident et **terminent des tâches** avec peu ou pas d'accompagnement.*

C'est le **plus gros bloc**, et c'est notre **plus gros décalage**.

Notre rendu vend une **soustraction** : « nous appelons moins le modèle ».
Le jury achète une **addition** : « quelle corvée réelle disparaît ».

Pire : notre démonstration montre surtout des **refus** — création de tâche
refusée sans confirmation, effacement de base refusé. Lu à travers ce critère,
« peu ou pas d'accompagnement », un garde-fou qui **exige une confirmation
humaine** ressemble à… de l'accompagnement. On peut nous compter notre plus
belle qualité en négatif.

**La reformulation qui sauve les 40 %** — et elle est vraie, pas cosmétique :

> La confirmation n'est pas un frein à l'autonomie. **C'est ce qui permet d'en
> accorder beaucoup.** On ne lâche pas mille agents sans surveillance dans une
> entreprise parce qu'on leur fait confiance ; on le fait parce que la porte
> qui compte ne dépend pas de leur humeur. La friction supprimée, c'est
> **l'humain qui n'a plus à relire chaque action** — pas l'appel de modèle
> économisé.

Il faut aussi **nommer une corvée réelle**. `read_carte`, `create_task`,
`drop_database` sont des noms de fonctions ; personne ne se les représente.
C'est exactement la leçon rapportée de CatapulZ dans l'étude v1, et le
règlement la confirme mot pour mot : *« résous un problème que tu as
vraiment »*.

### 🟡 30 % — « Architectural Discipline & Tech Stack »

> *…comment vous découplez les systèmes, **gérez l'état et la mémoire**,
> **sécurisez les identifiants**, et **traitez les pannes**.*

Deux trous, tous les deux nommés explicitement par le critère.

**a) Les identifiants — notre propre README montre la mauvaise pratique.**
Il écrit, en toutes lettres :

```
export GOOGLE_API_KEY=<your Gemini API key>
gcloud run deploy ... --set-env-vars GOOGLE_API_KEY=<key>
```

Une clé secrète passée **en ligne de commande** : elle reste dans l'historique
du terminal, dans les journaux de déploiement, et en clair sur le service.
Sous un critère qui dit littéralement « sécurisez les identifiants », **nous
documentons nous-mêmes ce qu'il ne faut pas faire.** La réponse attendue est
**Secret Manager** (le coffre à secrets de Google Cloud).

**b) L'état — la preuve s'évapore.** Vérifié en direct à 15h08 :

```
GET /metrics  ->  {"requests":0,"deterministic":0,"llm":0,
                   "refused":0,"model_calls":0,"trace":[]}
```

Le service répond bien (code 200, 2,4 secondes de réveil), mais **tous les
compteurs sont à zéro**. Ils vivent dans la mémoire du conteneur : Cloud Run
éteint le conteneur quand personne ne vient, et tout repart à zéro.

Or le README promet : *« Both counts are published at `/metrics`, so the claim
is a measurement, not a sentence in a README. »*

**Un juge qui ouvre l'adresse à froid voit zéro partout.** La phrase la plus
forte du rendu se retourne contre lui. Et « gérer l'état » est le mot même du
critère.

### 🟡 30 % — « Demo & Production Readiness »

> *On veut une démonstration **en direct, non montée**, un diagramme
> d'architecture **propre**, une installation reproductible, et une **preuve
> visible que ça tourne sur Google Cloud**.*

**a) La vidéo dure 1 minute 51.** Le règlement demande **environ 4 minutes**,
couvrant le problème, la valeur, et la démonstration en action. Nous sommes à
moins de la moitié.

**b) « en direct, non montée » — et notre vidéo est *dessinée*.**
`fabriquer_video.py` le dit lui-même en tête de fichier : *« The frames are
rendered rather than screen-grabbed, because the machine has no usable desktop
session. »* Une vidéo fabriquée image par image n'est pas une capture en
direct. C'est un risque réel sur ce critère.

**Et la raison invoquée n'est plus vraie.** Aujourd'hui, 31/08 à 14h35, la
capture d'écran du bureau a été **mesurée et prouvée sur ce poste** : 0,62
seconde par image, 3840 × 1080, image réelle. Le poste a maintenant une
session de bureau utilisable. **On peut filmer pour de vrai.**

**c) Le diagramme.** `architecture-diagram.md` est un dessin en caractères de
texte dans un fichier Markdown. Il est juste et lisible dans un terminal, mais
« diagramme propre » suggère une **image**. Sur la page du concours, un bloc de
texte brut ne se lit pas comme un schéma.

**d) La preuve Google Cloud** est là (`captures/cloud-run-console.jpg`,
`preuve-execution-cloud.txt`). ✅ Ce point est tenu.

---

## 3. Un point offert que nous ne prenons pas

Le règlement donne des **points bonus**, jusqu'à **+1,0** :

| Bonus | Points | Où nous en sommes |
|---|---|---|
| Publier un article/vidéo sur la fabrication, en public, en disant que c'est pour ce hackathon | +0,2 | rien |
| Publier sur X ou LinkedIn avec `#AllThingsAgenticHackathon` | +0,2 | rien |
| Ajouter d'autres modèles Google — Veo, Lyria, Gemma | +0,2 chacun, max +0,6 | rien |

**Le plus rapide est Gemma.** C'est un modèle Google **ouvert**, il tourne en
local — exactement là où `sgrm_selector.py` fait déjà tourner **Qwen**. Notre
`preuve-deux-modeles.txt` compare déjà « Gemini contre modèle local ».
**Remplacer Qwen par Gemma dans cette comparaison rapporte +0,2 et rend la
preuve plus cohérente** : deux modèles Google au lieu d'un Google et un chinois.

---

## 4. Ce qu'il ne faut PAS toucher

Le prédateur ne rapporte pas que des manques.

`audit_sgrm_hackathon.py` — un programme qui relit le rendu et **fait échouer
la construction** si une affirmation n'est pas confirmée par les fichiers —
est notre meilleure pièce, et elle est **rare**. Il a été écrit parce qu'une
version précédente annonçait une intégration Gemini que le code ne faisait
pas. C'est la pensée de la tour : **une porte qui refuse fait son travail.**

Il ne faut pas le supprimer parce qu'il vient de se tromper. Il faut **le
rendre plus dur** : qu'il rougisse sur le modèle (partie 1), et qu'il refuse
une conséquence qui ne s'appuie sur aucune mesure.

De même, les « Mandatory disclosures » et la « Honest limitation » du README
sont à **garder telles quelles**. Elles nous distinguent, et le règlement
demande explicitement *« vos constats et vos apprentissages »* — c'est là
qu'elles trouvent leur place officielle.

---

## 5. Les trois niveaux (règle du colonel)

- **Le geste (tactique)** — vérifier l'accès à Gemini 3.5, corriger le modèle,
  redéployer. Sans ça, tout le reste est décoratif.
- **La manœuvre (opérationnel)** — rendre les compteurs persistants (Firestore
  ferait d'une pierre deux coups : la preuve tient debout, **et** ça ajoute un
  deuxième service Google Cloud), passer la clé dans Secret Manager, refilmer
  en vrai à quatre minutes.
- **La raison (stratégique)** — le jury note « la friction enlevée tout seul ».
  Notre thèse ne doit plus être « nous appelons moins le modèle » mais :
  **le déterminisme est ce qui rend l'autonomie accordable en masse.**
  C'est la même vérité, dite du côté du gain.

---

## 6. L'ordre des onze heures

1. ~~Vérifier que Gemini 3.5 est accessible~~ — **FAIT le 31/08 à 15h05 :
   `gemini-3.5-flash` répond.**
2. **Corriger la liste des modèles** dans `gcp_router/main.py` et **redéployer**.
3. **Durcir le contrôle d'audit** : chercher dans le routeur, s'exclure
   lui-même, rougir tant que c'est faux.
4. **Refaire tourner `demo_flight.sh` sur le service** → nouvelles preuves
   portant un modèle conforme.
5. **Réécrire l'ouverture du README** côté friction enlevée, avec une corvée
   nommée.
6. **Sortir la clé du README** et documenter Secret Manager.
7. **Refilmer la démonstration en vrai**, à 4 minutes, écran non verrouillé.
8. **Rendre les compteurs persistants** — si le temps le permet.
9. **Bonus** : un post LinkedIn avec le mot-clic, et Gemma à la place de Qwen.

Les points 1 à 4 sont **vitaux**. Les 5 à 7 sont **rentables**.
Les 8 et 9 sont **du confort**.

---

## 7. Confiance

**0,95.**

Ce qui la tient : le règlement et les critères ont été lus **à la source**
(courriel officiel et page du concours), pas de mémoire. Chaque constat est
attaché à un fichier, une ligne, ou une réponse du service obtenue en direct.
La non-conformité du modèle est vérifiée à **trois** endroits indépendants.

Ce qui la retient : je n'ai pas relu le règlement
complet (« Full Rules »), seulement le courriel officiel et la page publique —
il peut y avoir une clause que je n'ai pas vue.

---

## 8. Les trois lignes

- **Fait** — Règlement, critères de notation, date limite et prix établis à la
  source. Neuf écarts constatés, dont **un qui met l'inscription en danger**
  (Gemini 2.5 au lieu de 3.5, vérifié à trois endroits) et **un vert menteur**
  dans notre propre auditeur. Le service tourne toujours. Rien n'a été modifié.
- **Suivant** — **Mettre `gemini-3.5-flash` en tête de la ligne 32 de
  `gcp_router/main.py`, redéployer, refaire tourner les preuves.** Le modèle a
  été testé et il répond : plus rien n'empêche ce geste.
- **Bloqué par** — **Patrick**, sur un seul point désormais : le feu vert pour
  toucher au code et redéployer. Braignak ne publie rien et ne modifie rien.
