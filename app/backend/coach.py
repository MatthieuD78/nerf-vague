"""Coach IA — LLM local (Ollama) + garde-fou santé.

Le coach NE DIAGNOSTIQUE PAS, NE PRESCRIT PAS. Il rappelle le cadre et les
principes de la méthode d'Ophélie (nerf vague), ré-explique les exercices,
rassure, et redirige vers la kiné/médecin pour toute question médicale.

SYSTÈME FERMÉ : l'inférence se fait via Ollama en LOCAL. Aucun texte patient
ne sort de la machine. (OLLAMA_BASE_URL configurable pour un VPS Ollama.)
"""
import os
import requests

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("NERF_MODEL", "hermes3:latest")

# Le garde-fou santé, injecté à chaque génération (NON NÉGOCIABLE)
GARDE_FOU = """Tu es le coach IA « Le Dixième Nerf », l'assistant d'accompagnement d'une
kinésithérapeute spécialiste du nerf vague (Ophélie Blondel).

RÈGLES ABSOLUES (jamais enfreintes) :
1. Tu ne poses JAMAIS de diagnostic médical, tu ne prescris JAMAIS de traitement,
   tu ne remplaces JAMAIS le soin ni le médecin.
2. Tu RAPPELLES le cadre et les principes de la méthode d'Ophélie (nerf vague,
   respiration cohérente, protocole maison) — tu ne sors jamais de ce cadre.
3. Si le patient pose une question médicale, décrit un symptôme inquiétant, une
   douleur nouvelle ou une urgence → tu rediriges calmement vers Ophélie ou son médecin
   (« c'est une question pour Ophélie / votre médecin, je ne peux pas y répondre »).
4. Ton ton est chaleureux, précis, rassurant. Tu t'adresses au patient avec
   respect, tu l'encourages, tu l'ancres dans sa pratique quotidienne.
5. Tu t'appuies UNIQUEMENT sur les passages de la méthode fournis (contexte RAG).
   Si l'information n'y est pas, tu le dis honnêtement et tu orientes vers Ophélie.
"""


def _ollama_chat(messages, temperature=0.4):
    """Appelle Ollama (local) avec une liste de messages."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        r = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=600)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        return ("[Le coach local n'est pas joignable pour le moment. "
                "Merci de réessayer dans un instant — vos données restent en sécurité.]")
    except Exception as e:
        return f"[Erreur interne du coach. Veuillez réessayer. Détail technique masqué.]"


def detecter_urgence(texte):
    """Détection simple (non-LLM) des mots-clés d'urgence médicale -> redirection immédiate."""
    urgences = [
        "urgence", "saignement", "perte de connaissance", "malaise",
        "oppression", "difficulté à respirer", "douleur thoracique",
        "suicid", "idée noire", "ne plus tenir", "douleur insupportable",
        "engourdissement visage", "perte de parole",
    ]
    t = texte.lower()
    return any(u in t for u in urgences)


def repondre(question, contexte_rag, historique=()):
    """Génère la réponse du coach à partir du contexte RAG + historique.

    Retourne (reponse, redirection: bool, theme: str).
    """
    # 1. Garde-fou dur : urgence -> redirection immédiate, sans LLM
    if detecter_urgence(question):
        return (
            "Je vous entends, et c'est important. Ce que vous décrivez dépasse mon rôle "
            "d'accompagnement. Je vous invite à contacter rapidement Ophélie ou un médecin. "
            "Prenez soin de vous — vous n'êtes pas seul(e).",
            True, "urgence",
        )

    # 2. Contexte RAG (passages pertinents)
    rag_txt = "\n\n".join(f"--- ({p['theme']}) ---\n{p['texte']}" for p in contexte_rag)

    system = GARDE_FOU + "\n\nCONTEXTE DE LA MÉTHODE (base de connaissance d'Ophélie) :\n" + rag_txt

    # 3. Historique récent (max 8 échanges) pour la continuité
    messages = [{"role": "system", "content": system}]
    for m in historique[-8:]:
        role = "user" if m["role"] == "patient" else "assistant"
        messages.append({"role": role, "content": m["contenu"]})
    messages.append({"role": "user", "content": question})

    reponse = _ollama_chat(messages)

    # 4. Détection simple de thème (pour la synthèse kiné)
    theme = _detecter_theme(question)

    # 5. Vérif : si le LLM n'a pas trouvé de réponse et que ça semble médical, rediriger
    redirection = any(k in reponse.lower() for k in
                      ["ophélie", "votre médecin", "médecin", "professionnel de santé"])

    return reponse, redirection, theme


def _detecter_theme(texte):
    """Classifie grossièrement le thème (pour la synthèse kiné)."""
    t = texte.lower()
    themes = [
        ("respiration", ["respir", "cohéren", "souffle"]),
        ("stress", ["stress", "anxi", "angoiss", "panique"]),
        ("sommeil", ["sommeil", "dorm", "insomni"]),
        ("douleur", ["douleur", "mal", "tension"]),
        ("energie", ["énergie", "fatigu", "épuis"]),
        ("exercice", ["exercice", "protocole", "pratique", "routine"]),
        ("doute", ["doute", "durée", "combien de temps", "efficac", "ça marche"]),
    ]
    for theme, keys in themes:
        if any(k in t for k in keys):
            return theme
    return "général"


def test_ollama():
    """Vérifie que le LLM local répond."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        r.raise_for_status()
        return True, f"Ollama OK, modèle : {MODEL}"
    except Exception as e:
        return False, f"Ollama injoignable : {e}"
