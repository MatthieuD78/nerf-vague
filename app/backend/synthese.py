"""Synthèse par patient — pour l'app kiné.

Regroupe les messages, ressentis et l'engagement du patient en une synthèse
lisible que la kiné consulte avant la séance. Les données restent des
DÉCLARATIONS du patient, jamais interprétées comme diagnostic.
"""
import db


def synthese_patient(patient_id):
    """Construit la synthèse structurée d'un patient."""
    conn = db.get_conn()
    pat = conn.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    if not pat:
        conn.close()
        return None
    pat = dict(pat)

    messages = db.get_messages(patient_id, limit=200)
    ressentis = db.get_ressentis(patient_id, limit=30)

    # --- Engagement ---
    nb_messages_patient = sum(1 for m in messages if m["role"] == "patient")
    nb_ressentis = len(ressentis)
    nb_exercices = sum(1 for r in ressentis if r["exercice_fait"])

    # --- Thèmes récurrents (questions du patient) ---
    themes = {}
    for m in messages:
        if m["role"] == "patient" and m.get("theme"):
            themes[m["theme"]] = themes.get(m["theme"], 0) + 1
    themes_tries = sorted(themes.items(), key=lambda x: -x[1])

    # --- Derniers ressentis (tendance simple) ---
    derniers = ressentis[-7:] if ressentis else []
    def moyenne(cle):
        vals = [r[cle] for r in derniers if r.get(cle) is not None]
        return round(sum(vals) / len(vals), 1) if vals else None

    tendance = {
        "stress": moyenne("stress"),
        "sommeil": moyenne("sommeil"),
        "douleur": moyenne("douleur"),
        "energie": moyenne("energie"),
    }

    # --- Signaux d'alerte (à signaler à la kiné) ---
    alertes = []
    if tendance["douleur"] is not None and tendance["douleur"] >= 7:
        alertes.append("douleur élevée rapportée")
    if tendance["stress"] is not None and tendance["stress"] >= 8:
        alertes.append("stress élevé rapporté")
    if tendance["sommeil"] is not None and tendance["sommeil"] <= 3:
        alertes.append("sommeil très perturbé")
    if nb_messages_patient == 0 and nb_ressentis == 0:
        alertes.append("aucune activité dans l'app")
    # doute exprimé
    for m in messages:
        if m["role"] == "patient" and m.get("theme") == "doute":
            alertes.append("doute/incertitude exprimé sur la méthode")
            break

    # --- Dernières questions du patient (extraits) ---
    questions = [m["contenu"] for m in messages if m["role"] == "patient"][-5:]

    conn.close()
    return {
        "patient": pat,
        "engagement": {
            "messages_patient": nb_messages_patient,
            "saisies_ressenti": nb_ressentis,
            "exercices_faits": nb_exercices,
        },
        "themes_frequents": themes_tries,
        "tendance_7j": tendance,
        "alertes": alertes,
        "dernieres_questions": questions,
    }
