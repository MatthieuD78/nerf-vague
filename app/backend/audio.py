"""Transcription audio LOCALE des enregistrements (notes vocales kiné / app patient).

SYSTÈME FERMÉ : la transcription utilise faster-whisper (modèle local, rien ne sort).
La synthèse pour continuité du soin utilise le LLM local (Ollama) via coach.
"""
import os

# Modèle whisper local (petit mais bon rapport qualité/vitesse pour la voix)
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
_local_whisper = None


def _get_whisper():
    global _local_whisper
    if _local_whisper is None:
        from faster_whisper import WhisperModel
        # CPU, int8 pour la vitesse ; modèle local téléchargé au 1er usage
        _local_whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _local_whisper


def transcrire(fichier_audio: str, langue="fr") -> str:
    """Transcrit un fichier audio en texte, en local. Retourne '' si échec."""
    try:
        if not os.path.exists(fichier_audio):
            return ""
        model = _get_whisper()
        segments, _info = model.transcribe(fichier_audio, language=langue)
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()
    except Exception as e:
        # ne pas faire échouer l'app si la transcription échoue : message clair
        return f"[Transcription locale indisponible : {type(e).__name__}]"


def synthetiser_continuité(transcription: str) -> str:
    """Résume une note vocale pour la continuité du soin, via le LLM local.

    Donne à la kiné l'essentiel à retenir (sans interpréter médicalement).
    """
    if not transcription or transcription.startswith("["):
        return ""
    import coach
    system_hint = (
        "Résume cette note vocale de kinésithérapie pour la continuité du soin. "
        "Extrais : les points clés, les ressentis/déclarations du patient, les actions "
        "à retenir pour la prochaine séance. Reste factuel (déclarations, pas diagnostic), "
        "concis (5-7 lignes max), en français."
    )
    # court appel au LLM local (système fermé)
    try:
        from coach import _ollama_chat
        reponse = _ollama_chat([
            {"role": "system", "content": system_hint},
            {"role": "user", "content": transcription},
        ], temperature=0.3)
        # découpe du "[Err" éventuel
        if reponse.startswith("[Erreur") or reponse.startswith("[Le"):
            return ""
        return reponse.strip()
    except Exception:
        return ""
