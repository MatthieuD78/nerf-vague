"""RAG — indexation et recherche sur la base de connaissances nerf vague.

Indexe les documents .md du dossier knowledge/ dans ChromaDB (local),
puis permet de retrouver les passages pertinents pour répondre au patient.
TOUT est local (ChromaDB persisté sur disque) — système fermé respecté.
"""
import os
import glob
import chromadb
from chromadb.utils import embedding_functions

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# Embeddings : tout en local (aucun appel réseau). On utilise l'embedding par défaut
# de Chroma (Onnx MiniLM, tourne localement) pour respecter le système fermé.
_ef = embedding_functions.DefaultEmbeddingFunction()

_client = chromadb.PersistentClient(path=CHROMA_DIR)


def _collection():
    return _client.get_or_create_collection(
        name="nerf_vague_knowledge",
        embedding_function=_ef,
        metadata={"hnsw:space": "cosine"},
    )


def _load_documents():
    """Retourne [(id, contenu, metadonnées)] depuis tous les .md de knowledge/."""
    docs = []
    for path in sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "**", "*.md"), recursive=True)):
        rel = os.path.relpath(path, KNOWLEDGE_DIR)
        # ignorer l'index et la couche scientifique (non validée)
        if rel.startswith("_index") or rel.startswith("06-recherche"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except Exception:
            continue
        # thème = premier segment du chemin
        theme = rel.split(os.sep)[0]
        docs.append({
            "id": rel.replace(os.sep, "__").replace(".md", ""),
            "text": text,
            "meta": {"theme": theme, "fichier": rel},
        })
    return docs


def indexer(force=False):
    """Indexe les documents dans ChromaDB. Retourne le nombre de chunks."""
    col = _collection()
    if not force and col.count() > 0:
        return col.count()
    docs = _load_documents()
    if not docs:
        return 0
    # Découpage simple par paragraphe/section (le RAG santé reste lisible)
    ids, texts, metas = [], [], []
    for d in docs:
        # découper en blocs de ~800 chars sur les sauts de ligne
        blocs = _chunk(d["text"], 800)
        for i, b in enumerate(blocs):
            ids.append(f"{d['id']}__{i}")
            texts.append(b)
            metas.append(d["meta"])
    # Réinitialiser et réinsérer proprement
    existing = col.get()["ids"]
    if existing:
        col.delete(ids=existing)
    if ids:
        col.add(ids=ids, documents=texts, metadatas=metas)
    return len(ids)


def _chunk(text, size):
    """Découpe un texte en blocs d'environ `size` caractères, sur les sauts de paragraphe."""
    text = text.strip()
    if len(text) <= size:
        return [text]
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 > size and cur:
            chunks.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks or [text[:size]]


def rechercher(query, n=4):
    """Retourne les passages les plus pertinents pour une question."""
    col = _collection()
    res = col.query(query_texts=[query], n_results=n)
    passages = []
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    for i, doc in enumerate(docs):
        passages.append({
            "texte": doc,
            "theme": metas[i]["theme"] if i < len(metas) else "",
            "distance": round(dists[i], 3) if i < len(dists) else None,
        })
    return passages


def stats():
    col = _collection()
    return {"chunks_indexés": col.count()}
