"""RAG-Engine: Dokument-Chunking, Embedding via Gemini, Suche via ChromaDB."""
import io
import os
import uuid

import PyPDF2
import chromadb
from google import genai
from google.genai import types

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EMBED_MODEL = "text-embedding-004"
GEN_MODEL = "gemini-1.5-flash"

_client: chromadb.Client | None = None
_collection: chromadb.Collection | None = None


def _chroma():
    global _client, _collection
    if _collection is None:
        _client = chromadb.Client()
        _collection = _client.get_or_create_collection("dokumente")
    return _collection


def _genai() -> genai.Client:
    return genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


def _chunk_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if len(c) > 50]


def _embed(texts: list[str]) -> list[list[float]]:
    client = _genai()
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return [e.values for e in result.embeddings]


def dokument_laden(inhalt: bytes, dateiname: str) -> int:
    if dateiname.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(inhalt))
        text = "\n".join(s.extract_text() or "" for s in reader.pages)
    else:
        text = inhalt.decode("utf-8", errors="ignore")

    chunks = _chunk_text(text)
    embeddings = _embed(chunks)
    col = _chroma()

    ids = [str(uuid.uuid4()) for _ in chunks]
    col.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"quelle": dateiname, "chunk": i} for i in range(len(chunks))],
    )
    return len(chunks)


def fragen(frage: str, top_k: int = 4) -> dict:
    client = _genai()
    col = _chroma()

    if col.count() == 0:
        return {"antwort": "Bitte zuerst ein Dokument hochladen.", "quellen": []}

    q_embed = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[frage],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values

    ergebnis = col.query(query_embeddings=[q_embed], n_results=min(top_k, col.count()))
    kontext_chunks = ergebnis["documents"][0]
    quellen = [m["quelle"] for m in ergebnis["metadatas"][0]]

    kontext = "\n\n---\n\n".join(kontext_chunks)
    prompt = (
        f"Beantworte die Frage ausschließlich auf Basis des folgenden Kontexts.\n"
        f"Wenn die Antwort nicht im Kontext steht, sage das ehrlich.\n\n"
        f"Kontext:\n{kontext}\n\n"
        f"Frage: {frage}"
    )

    antwort = client.models.generate_content(
        model=GEN_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1),
    )
    return {"antwort": antwort.text, "quellen": list(dict.fromkeys(quellen))}


def kollektion_leeren() -> None:
    global _collection
    if _collection:
        _client.delete_collection("dokumente")
        _collection = _client.get_or_create_collection("dokumente")
