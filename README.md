# RAG Document Q&A

PDF oder Text hochladen und mit KI Fragen stellen — Antworten mit Quellenangabe.

**Live:** https://rag-document-qa-api-318293260539.europe-west3.run.app

## Stack

- **Backend**: Python · FastAPI · ChromaDB · Gemini Embeddings (`text-embedding-004`) · Gemini Flash
- **Frontend**: React · TypeScript · Tailwind CSS · Vite
- **Deployment**: Render

## Features

- PDF, TXT und Markdown Upload
- Automatisches Chunking und Embedding
- Semantische Suche via ChromaDB
- Antwort mit Quellenangabe (welches Dokument, welcher Abschnitt)
- Vollständig lokal — keine externe Vektordatenbank nötig

## Lokale Entwicklung

```bash
# Backend
cd backend
pip install -r requirements.txt
export GOOGLE_API_KEY=dein-key
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Tests

```bash
pip install pytest httpx
pytest tests/ -v
```
