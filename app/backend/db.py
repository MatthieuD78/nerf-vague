"""Base de données SQLite — Le Dixième Nerf (app coach + app kiné).

Système fermé santé : données cloisonnées par kiné. Un kiné ne voit que SES patients.
Les données de santé sont locales (SQLite), jamais envoyées vers un service externe.
"""
import sqlite3
import os
import time
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "nerf-vague.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS kines (
        id TEXT PRIMARY KEY,
        nom TEXT NOT NULL,
        email TEXT UNIQUE,
        cree_le REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        kine_id TEXT NOT NULL REFERENCES kines(id),
        pseudo TEXT NOT NULL,          -- prénom/alias (minimisation)
        cree_le REAL NOT NULL,
        -- suivi de santé déclaré (jamais interprété comme diagnostic)
        objectif TEXT DEFAULT '',
        notes_kine TEXT DEFAULT ''     -- notes internes de la kiné
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL REFERENCES patients(id),
        role TEXT NOT NULL,            -- 'patient' ou 'coach'
        contenu TEXT NOT NULL,
        theme TEXT DEFAULT '',         -- thème détecté (respiration, stress, etc.)
        horodatage REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ressentis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL REFERENCES patients(id),
        jour TEXT NOT NULL,            -- date ISO YYYY-MM-DD
        stress INTEGER,                -- 0-10 (déclaré)
        sommeil INTEGER,               -- 0-10
        douleur INTEGER,               -- 0-10
        energie INTEGER,               -- 0-10
        exercice_fait INTEGER DEFAULT 0,  -- 0/1
        commentaire TEXT DEFAULT '',
        horodatage REAL NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_messages_patient ON messages(patient_id, horodatage);
    CREATE INDEX IF NOT EXISTS idx_ressentis_patient ON ressentis(patient_id, jour);
    """)
    conn.commit()
    conn.close()


# ---- Helpers ----
def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def ensure_kine(nom="Ophélie Blondel", email="ophlie@dixieme-nerf.fr"):
    """Crée la kiné par défaut si absente. (En prod : authentification réelle.)"""
    conn = get_conn()
    row = conn.execute("SELECT id FROM kines LIMIT 1").fetchone()
    if row:
        conn.close()
        return row["id"]
    kid = new_id("kine")
    conn.execute("INSERT INTO kines (id, nom, email, cree_le) VALUES (?,?,?,?)",
                 (kid, nom, email, time.time()))
    conn.commit()
    conn.close()
    return kid


def create_patient(kine_id, pseudo, objectif=""):
    conn = get_conn()
    pid = new_id("pat")
    conn.execute("INSERT INTO patients (id, kine_id, pseudo, cree_le, objectif) VALUES (?,?,?,?,?)",
                 (pid, kine_id, pseudo, time.time(), objectif))
    conn.commit()
    conn.close()
    return pid


def list_patients(kine_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM patients WHERE kine_id=? ORDER BY cree_le DESC",
                        (kine_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_message(patient_id, role, contenu, theme=""):
    conn = get_conn()
    cur = conn.execute("INSERT INTO messages (patient_id, role, contenu, theme, horodatage) "
                       "VALUES (?,?,?,?,?)", (patient_id, role, contenu, theme, time.time()))
    conn.commit()
    conn.close()
    return cur.lastrowid


def add_ressenti(patient_id, jour, stress, sommeil, douleur, energie,
                 exercice_fait=0, commentaire=""):
    conn = get_conn()
    # upsert : un ressenti par jour et par patient
    existing = conn.execute("SELECT id FROM ressentis WHERE patient_id=? AND jour=?",
                            (patient_id, jour)).fetchone()
    if existing:
        conn.execute("""UPDATE ressentis SET stress=?, sommeil=?, douleur=?, energie=?,
                        exercice_fait=?, commentaire=?, horodatage=? WHERE id=?""",
                     (stress, sommeil, douleur, energie, exercice_fait, commentaire,
                      time.time(), existing["id"]))
    else:
        conn.execute("""INSERT INTO ressentis (patient_id, jour, stress, sommeil, douleur,
                        energie, exercice_fait, commentaire, horodatage)
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                     (patient_id, jour, stress, sommeil, douleur, energie,
                      exercice_fait, commentaire, time.time()))
    conn.commit()
    conn.close()


def get_messages(patient_id, limit=50):
    conn = get_conn()
    rows = conn.execute("""SELECT role, contenu, theme, horodatage FROM messages
                           WHERE patient_id=? ORDER BY id DESC LIMIT ?""",
                        (patient_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def get_ressentis(patient_id, limit=30):
    conn = get_conn()
    rows = conn.execute("""SELECT jour, stress, sommeil, douleur, energie, exercice_fait,
                           commentaire FROM ressentis WHERE patient_id=?
                           ORDER BY jour DESC LIMIT ?""", (patient_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]
