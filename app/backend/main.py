"""Le Dixième Nerf — API backend (système fermé santé).

Routes :
- Patient : /api/patient/chat, /api/patient/ressenti, /api/patient/etat
- Kiné : /api/kine/patients, /api/kine/synthese/<id>, /api/kine/tableau
- Santé : /api/sante
"""
import os
from datetime import date

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import db
import rag
import coach
import synthese
import audio
import shutil
import time
from datetime import date as _date

app = FastAPI(title="Le Dixième Nerf — API coach", version="1.0")

# CORS ouvert pour les frontends locaux (frontend-patient, frontend-kine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod : restreindre aux domaines du kiné
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.path.dirname(__file__)
APP_DIR = os.path.join(BASE, "..")
# Dossier de stockage local des fichiers (photos + audio) — système fermé
UPLOAD_DIR = os.path.join(BASE, "stockage")
for sub in ("photos", "audio"):
    os.makedirs(os.path.join(UPLOAD_DIR, sub), exist_ok=True)
# servir les fichiers stockés (accès local à l'app)
app.mount("/stockage", StaticFiles(directory=UPLOAD_DIR), name="stockage")


# ---------- Schémas ----------
class ChatIn(BaseModel):
    patient_id: str
    message: str


class RessentiIn(BaseModel):
    patient_id: str
    stress: int | None = None
    sommeil: int | None = None
    douleur: int | None = None
    energie: int | None = None
    exercice_fait: int = 0
    commentaire: str = ""


class PatientIn(BaseModel):
    pseudo: str
    objectif: str = ""
    type_soin: str = "HN"


class BilanIn(BaseModel):
    titre: str
    contenu: str = ""
    date_bilan: str = ""


class PhotoIn(BaseModel):
    fichier: str
    legende: str = ""
    date_photo: str = ""


class ObjectifIn(BaseModel):
    objectif: str
    date_obj: str = ""
    statut: str = "en_cours"


class ObjectifStatut(BaseModel):
    statut: str


class EnregistrementIn(BaseModel):
    fichier: str
    note: str = ""
    date_audio: str = ""


# ---------- Démarrage ----------
@app.on_event("startup")
def _startup():
    db.init_db()
    db.ensure_kine()
    # Indexer le RAG au démarrage si vide
    try:
        n = rag.indexer(force=False)
        print(f"[RAG] {n} chunks indexés")
    except Exception as e:
        print(f"[RAG] erreur indexation : {e}")


# ---------- Santé ----------
@app.get("/api/sante")
def sante():
    ok, msg = coach.test_ollama()
    return {
        "statut": "ok",
        "ollama": ok,
        "ollama_detail": msg,
        "rag": rag.stats(),
    }


# ---------- Patient ----------
@app.post("/api/patient/chat")
def chat(inp: ChatIn):
    pat = _get_patient(inp.patient_id)
    # enregistrer le message du patient
    db.add_message(inp.patient_id, "patient", inp.message, theme=coach._detecter_theme(inp.message))
    # récupérer le contexte RAG
    contexte = rag.rechercher(inp.message, n=4)
    historique = db.get_messages(inp.patient_id, limit=20)
    reponse, redirection, theme = coach.repondre(inp.message, contexte, historique)
    # enregistrer la réponse du coach
    db.add_message(inp.patient_id, "coach", reponse, theme=theme)
    return {"reponse": reponse, "redirection": redirection, "theme": theme}


@app.post("/api/patient/ressenti")
def ressenti(inp: RessentiIn):
    _get_patient(inp.patient_id)
    db.add_ressenti(inp.patient_id, date.today().isoformat(), inp.stress, inp.sommeil,
                    inp.douleur, inp.energie, inp.exercice_fait, inp.commentaire)
    return {"ok": True}


@app.get("/api/patient/etat")
def etat(patient_id: str):
    pat = _get_patient(patient_id)
    messages = db.get_messages(patient_id, limit=30)
    ressentis = db.get_ressentis(patient_id, limit=14)
    return {"patient": pat, "messages": messages, "ressentis": ressentis}


# ---------- Kiné ----------
@app.get("/api/kine/patients")
def kine_patients():
    kine_id = db.ensure_kine()
    return db.list_patients(kine_id)


@app.post("/api/kine/patients")
def kine_create(inp: PatientIn):
    kine_id = db.ensure_kine()
    pid = db.create_patient(kine_id, inp.pseudo, inp.objectif, inp.type_soin)
    return {"id": pid}


@app.get("/api/kine/synthese/{patient_id}")
def kine_synthese(patient_id: str):
    s = synthese.synthese_patient(patient_id)
    if not s:
        raise HTTPException(404, "Patient introuvable")
    return s


@app.get("/api/kine/tableau")
def kine_tableau():
    kine_id = db.ensure_kine()
    patients = db.list_patients(kine_id)
    tableau = []
    for p in patients:
        s = synthese.synthese_patient(p["id"])
        tableau.append({
            "id": p["id"],
            "pseudo": p["pseudo"],
            "objectif": p["objectif"],
            "type_soin": p.get("type_soin", "HN"),
            "engagement": s["engagement"] if s else None,
            "alertes": s["alertes"] if s else [],
            "tendance": s["tendance_7j"] if s else None,
        })
    return tableau


# ---------- Dossier patient complet (bilans, photos, objectifs, audio) ----------
@app.post("/api/kine/patients/{patient_id}/bilan")
def add_bilan(patient_id: str, inp: BilanIn):
    _get_patient(patient_id)
    db.add_bilan(patient_id, inp.titre, inp.contenu, inp.date_bilan or _today())
    return {"ok": True}


@app.get("/api/kine/patients/{patient_id}/bilans")
def get_bilans(patient_id: str):
    _get_patient(patient_id)
    return db.get_bilans(patient_id)


@app.post("/api/kine/patients/{patient_id}/photo")
async def upload_photo(patient_id: str, fichier: UploadFile = File(...), legende: str = Form("")):
    """Upload d'une photo : sauvegarde locale + enregistre en DB. Système fermé."""
    _get_patient(patient_id)
    ext = os.path.splitext(fichier.filename or "")[1] or ".jpg"
    nom_fichier = f"{patient_id}_{int(time.time())}{ext}"
    dest = os.path.join(UPLOAD_DIR, "photos", nom_fichier)
    with open(dest, "wb") as f:
        shutil.copyfileobj(fichier.file, f)
    url = f"/stockage/photos/{nom_fichier}"
    db.add_photo(patient_id, url, legende, _today())
    return {"ok": True, "fichier": url}


@app.get("/api/kine/patients/{patient_id}/photos")
def get_photos(patient_id: str):
    _get_patient(patient_id)
    return db.get_photos(patient_id)


@app.post("/api/kine/patients/{patient_id}/objectif")
def add_objectif(patient_id: str, inp: ObjectifIn):
    _get_patient(patient_id)
    db.add_objectif(patient_id, inp.objectif, inp.date_obj or _today(), inp.statut)
    return {"ok": True}


@app.patch("/api/kine/objectifs/{objectif_id}")
def set_objectif_statut(objectif_id: str, inp: ObjectifStatut):
    db.set_objectif_statut(objectif_id, inp.statut)
    return {"ok": True}


@app.get("/api/kine/patients/{patient_id}/objectifs")
def get_objectifs(patient_id: str):
    _get_patient(patient_id)
    return db.get_objectifs(patient_id)


@app.post("/api/kine/patients/{patient_id}/enregistrement")
async def upload_enregistrement(patient_id: str, fichier: UploadFile = File(...),
                                note: str = Form(""), date_audio: str = Form("")):
    """Upload d'un enregistrement audio : sauvegarde locale + transcription locale (whisper)
    + synthèse pour continuité. Système fermé (rien ne sort)."""
    _get_patient(patient_id)
    ext = os.path.splitext(fichier.filename or "")[1] or ".m4a"
    nom_fichier = f"{patient_id}_{int(time.time())}{ext}"
    dest = os.path.join(UPLOAD_DIR, "audio", nom_fichier)
    with open(dest, "wb") as f:
        shutil.copyfileobj(fichier.file, f)
    # transcription en local (faster-whisper)
    transcription = audio.transcrire(dest, langue="fr")
    synthese_cont = audio.synthetiser_continuité(transcription) if transcription else ""
    url = f"/stockage/audio/{nom_fichier}"
    db.add_enregistrement(patient_id, url, transcription, synthese_cont,
                          note, date_audio or _today())
    return {"ok": True, "fichier": url, "transcription": transcription, "synthese": synthese_cont}


@app.get("/api/kine/patients/{patient_id}/enregistrements")
def get_enregistrements(patient_id: str):
    _get_patient(patient_id)
    return db.get_enregistrements(patient_id)


@app.get("/api/kine/patients/{patient_id}/dossier")
def get_dossier(patient_id: str):
    """Dossier patient complet : infos + bilans + photos + objectifs + enregistrements + synthèse app."""
    pat = _get_patient(patient_id)
    return {
        "patient": pat,
        "bilans": db.get_bilans(patient_id),
        "photos": db.get_photos(patient_id),
        "objectifs": db.get_objectifs(patient_id),
        "enregistrements": db.get_enregistrements(patient_id),
        "synthese_app": synthese.synthese_patient(patient_id),
    }


def _today():
    return _date.today().isoformat()


# ---------- Helpers ----------
def _get_patient(patient_id):
    conn = db.get_conn()
    pat = conn.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    conn.close()
    if not pat:
        raise HTTPException(404, "Patient introuvable")
    return dict(pat)


# ---------- Frontends statiques ----------
@app.on_event("startup")
def _mount_frontends():
    # servir les frontends depuis la racine
    front_patient = os.path.join(APP_DIR, "frontend-patient")
    front_kine = os.path.join(APP_DIR, "frontend-kine")
    if os.path.isdir(front_patient):
        app.mount("/patient", StaticFiles(directory=front_patient, html=True), name="patient")
    if os.path.isdir(front_kine):
        app.mount("/kine", StaticFiles(directory=front_kine, html=True), name="kine")
