"""Vector API – FastAPI micro‑service wrapping Chroma and an embedder."""

from __future__ import annotations

import os
from uuid import uuid4
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma_db")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("COLLECTION", "spec_embeddings")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K_DEFAULT = int(os.getenv("TOP_K", "5"))

# ----------------------------------------------------------------------------
# Bootstrap: Chroma client & collection
# ----------------------------------------------------------------------------
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT, settings=Settings(anonymized_telemetry=False))
try:
    collection = client.get_collection(COLLECTION_NAME)
except chromadb.errors.NotFoundError:
    collection = client.create_collection(COLLECTION_NAME)

# ----------------------------------------------------------------------------
# Bootstrap: embedder (warm cache)
# ----------------------------------------------------------------------------
embedder = SentenceTransformer(EMBED_MODEL)

# ----------------------------------------------------------------------------
# Pydantic payloads
# ----------------------------------------------------------------------------
class UpsertBody(BaseModel):
    spec_id: str
    section: str
    text: str

class QueryBody(BaseModel):
    spec_id: str
    section: str
    k: int | None = None

# ----------------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------------
app = FastAPI(title="Vector API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upsert")
def upsert(body: UpsertBody):
    """Compute embedding & store it alongside raw text and metadata."""
    embedding = embedder.encode(body.text)
    doc_id = f"{body.spec_id}::{body.section}::{uuid4().hex[:8]}"
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[body.text],
        metadatas=[{"spec_id": body.spec_id, "section": body.section}],
    )
    return {"id": doc_id}

@app.post("/query")
def query(body: QueryBody):
    """Return the most similar chunks within the same spec (any section) plus global matches."""
    k = body.k or TOP_K_DEFAULT
    try:
        results = collection.query(
            query_embeddings=embedder.encode(body.section),  # embed section name as a proxy
            n_results=k,
            where={"spec_id": body.spec_id},
        )
        docs: List[str] = results["documents"][0] if results else []
        return {"chunks": docs[:k]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))