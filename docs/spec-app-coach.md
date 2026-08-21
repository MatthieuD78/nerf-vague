# 🧠 Le Dixième Nerf — SPEC de l'app coach IA (nerf vague)

> **Le cœur de la nouvelle offre** : une nouvelle forme d'accompagnement sur la base
> du nerf vague (le point de rencontre de toutes les formations du kiné).
> **Deux apps** : 1 pour le patient (coach IA), 1 pour le kiné (synthèse).

---

## 1. Le concept

Le kiné (Ophélie Blondel) a une **expertise** : le nerf vague, au croisement de ses formations
(stimulation vagale, drainage, técar, ondes de choc, cryothérapie). L'objectif est de
**prolonger le soin hors du cabinet** grâce à un **coach IA patient**, basé sur un **RAG**
(retrieval) **construit à partir de SES formations et de sa méthode**.

### Le couple (comme ÉLAN/KETO)
- **Au cabinet** : le soin manuel (le kiné, l'humain).
- **Hors cabinet** : l'**app coach IA** qui accompagne, rassure, guide le patient entre les séances.
- **Pour le kiné** : une **app praticienne** qui synthétise les échanges/travail de chacun de ses patients.

---

## 2. Le principe (pourquoi c'est unique et différenciant)

> La concurrence HN vend une technique. **Le Dixième Nerf vend un accompagnement continu**, 
> le soin ne s'arrête pas à la porte du cabinet.

- Le patient ne reste jamais seul entre deux séances.
- Le coach IA **reflète la méthode du kiné** (les vrais contenus de ses formations, pas du générique).
- Le kiné a une **vue d'ensemble** : il sait qui avance, qui stagne, qui a besoin d'un coup de main.

### 🎯 LE RÔLE DU COACH = RAPPELER LE CADRE (positionnement acté)

**C'est du SOIN** et le coach ne conseille pas librement : il **rappelle le cadre et les principes**
de la méthode ou de l'exercice utilisé par Ophélie.

Le coach ré-explique, ré-ancre, guide la répétition — il **ne sort jamais du cadre posé par le kiné** :
- rappel des exercices et de la respiration cohérente (comme en séance)
- rappel des principes du protocole (Évaluer → Activer → Ancrer)
- rappel des repères et ressources maison validées par Ophélie
- s'il reçoit une question hors de ce cadre (symptôme, diagnostic, traitement) → redirection vers Ophélie / le médecin

**Conséquence (positive)** : moins de risque (le coach reste dans la méthode du pro), plus de
cohérence (il ancre ce que la kiné a déjà dit), zéro dérive en « mini-médecin ».

### 📋 LE COACH CAPTE ET SYNTHÉTISE (la boucle avec la kiné)

En plus de rappeler le cadre, le coach **note ce que le patient dit** (entre les séances) :
- les **questions** qu'il pose (thèmes qui reviennent, incompréhensions)
- ses **ressentis** (stress, sommeil, douleur, énergie — déclarés, jamais interprétés comme diagnostic)
- ses **doutes** et hésitations (adhésion à la méthode, peurs)
- son **engagement** (fréquence d'utilisation, exercices suivis, régularité)

**Ce que cela produit** : une **synthèse de l'engagement hors cabinet** par patient, que la kiné
consulte avant la prochaine séance.
> Ex. : « Marc a utilisé l'app 6 fois cette semaine, surtout la respiration. Il a demandé 2 fois
> si son anxiété allait diminuer, et a exprimé un doute sur la durée. »

**Objectif** : la kiné arrive en séance en connaissant déjà les leviers et blocages du patient
→ séance personnalisée, lien renforcé, et le patient se sent réellement accompagné.

**Précision (garde-fou)** : ce sont des **déclarations du patient**, résumées fidèlement.
Le coach ne les interprète jamais en diagnostic — il les transmet brutes et structurées.

---

## 3. L'APP COACH IA PATIENT (l'outil des patients)

### Fonctions
- **Chat coach** : le patient pose ses questions, le coach répond selon le RAG des formations + méthode
- **Suivi quotidien** : ressenti, stress, sommeil, douleur, exercices vagals (respir. cohérente…)
- **Exercices guidés** : protocoles maison du kiné (respiration, stimulations douces, auto-régulation)
- **Garde-fou santé** : jamais de diagnostic ni de remplacement du soin — oriente vers le pro

### Le RAG
- **Base de connaissances** : les contenus des formations du kiné (nerf vague, drainage, técar, ondes de choc, cryo)
- **Règles de prudence** : produits santé → orientation vers le kiné/médecin, jamais invention

### L'expérience
- Le coach parle de façon **rassurante, précise, incarnée** (la voix d'une accompagnante experte)
- « Vous n'êtes pas seul(e) entre les séances » → réassurance + engagement

---

## 4. L'APP PRATICIENNE (l'outil du kiné)

### Fonctions
- **Synthèse par patient** : l'app résume les échanges + le travail réalisé dans le coach IA
- **Tableau de bord** : chacun de ses patients (avancée, engagement, signaux d'alerte)
- **Alertes** : un patient qui stagne ou exprime une inquiétude → signalé au kiné
- **Aide à la séance** : le kiné voit ce que le patient a fait en amont pour adapter le soin

### 🧭 ÉLARGISSEMENT ACTÉ (v2) — dossier patient COMPLET (HN + remboursés)

L'app kiné ne couvre plus seulement les patients de l'app coach : elle devient le
**dossier patient complet** pour TOUS les patients du kiné (HN ET conventionnels/remboursés),
pour la **continuité du soin dans le temps**.

Pour CHAQUE patient, l'app kiné regroupe :
- 📋 **Bilans** (bilan initial, bilans d'étape, notes cliniques)
- 📸 **Photos** (posture, cicatrices, évolution — datées)
- 🎯 **Objectifs de soin** (fixés, suivis, mis à jour)
- 💬 **Ressentis** (du patient : stress, douleur, sommeil, énergie — déclarés)
- 🎙️ **Enregistrements audio RETRANSCRITS** (séances/notes vocales du kiné) + synthèse
- 🤖 **Synthèse coach IA** : le coach retranscrit et synthétise les expressions du patient
  via l'app patient (boucle de capture) → la kiné voit ce que le patient a dit/ressenti

**Lien clé coach→kiné** : le coach IA centralise les expressions du patient (app patient)
et les **résume en synthèse** que la kiné consulte dans le dossier → continuité du soin.

> **Système fermé (rappel) :** les enregistrements audio et photos sont des données de
> santé → stockage local, transcription audio en LOCAL (whisper), jamais expédiés au cloud.

> **Valeur** : le kiné gagne du temps, personnalise ses séances, et garde le lien entre les RDV.

---

## 5. ARCHITECTURE TECHNIQUE (réutiliser le pipeline éprouvé de KETO)

### 🔒 SYSTÈME FERMÉ (exigence santé / secret pro — NON NÉGOCIABLE)

Les données de santé des patients **ne doivent jamais sortir** du système contrôlé par le kiné.

**3 verrous obligatoires :**
1. **Garde-fou strict** : le coach ne fait JAMAIS de diagnostic ni de prescription. Toute question
   médicale sérieuse redirige vers le kiné/médecin (« demandez à Ophélie »). Le coach guide, rassure,
   éduque — il ne soigne pas seul.
2. **Aucune donnée de santé sortante** : le texte du patient n'est JAMAIS envoyé vers un LLM cloud.
   → **LLM LOCAL (Ollama / llama.cpp)** : l'inférence se fait sur l'infrastructure du kiné, rien ne part.
3. **Secret professionnel** : chaque kiné ne voit que SES patients. Données chiffrées, cloisonnées,
   accessibles uniquement au praticien (et au patient concerné). Jamais de croisement.

**Structure fermée :**
```
Patient (app) ─┐
              ├─► API coach IA (locales)
Kiné (app)  ───┘      │
                      ├── RAG local (ChromaDB) — formations/méthode du kiné
                      ├── LLM LOCAL (Ollama) — l'inférence reste sur la machine
                      └── Garde-fou santé dur (orientation vers le pro)
                      └── Données : cloisonnées par kiné, chiffrées au repos
```

**Choix honnête (tension simplicité/fermeture) :**
- KETO (bien-être) → LLM cloud = simple et OK.
- **Nerf vague (santé) → LLM local obligatoire** = plus exigeant, mais c'est ÇA qui respecte
  les prérogatives d'une profession de santé et le secret pro. L'infra Ollama est déjà sur
  la machine (modèle local) → l'architecture fermée est faisable.

### Confidentialité / RGPD (santé — très strict)
- Données de santé **sensibles** → hébergement conforme, consentement explicite, minimisation
- Texte des patients **jamais hors de l'infra du kiné** (pas de LLM cloud)
- Le kiné ne voit que ses patients, chiffrement au repos

---

## 6. Ce qu'on peut RÉUTILISER de KETO (déjà construit)
- Le **backend RAG** (coach.py, main.py) — à adapter au nerf vague
- Le **garde-fou santé** (principe identique)
- Le **frontend app** (structure chat + suivi)
- La **méthode ChromaDB local + LLM OpenRouter** (coût maîtrisé)

=> On adapte, on ne repart pas de zéro.

---

## 7. PROCHAINES ÉTAPES (proposées)
1. **Structurer la base de connaissances nerf vague** (à partir des formations du kiné)
2. **Adapter le backend RAG** → « coach nerf vague »
3. **Construire l'app patient** (chat + suivi + exercices)
4. **Construire l'app praticienne** (synthèses par patient)
5. **Garde-fou santé + RGPD** (dès le début)
6. Déployer / tester

---

*Spec v1 · Les Éditions ÉLAN (écosystème) · Ophélie Blondel · À faire évoluer*
