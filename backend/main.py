from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import dokument_laden, fragen, kollektion_leeren

app = FastAPI(title="RAG Document Q&A")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174",
                   "https://rag-document-qa-ui.onrender.com"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


class FrageRequest(BaseModel):
    frage: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/dokument")
async def dokument_hochladen(datei: UploadFile = File(...)):
    erlaubt = {".pdf", ".txt", ".md"}
    suffix = "." + datei.filename.rsplit(".", 1)[-1].lower()
    if suffix not in erlaubt:
        raise HTTPException(400, f"Nur {', '.join(erlaubt)} erlaubt.")
    inhalt = await datei.read()
    if len(inhalt) > 10 * 1024 * 1024:
        raise HTTPException(400, "Datei zu groß (max. 10 MB).")
    anzahl = dokument_laden(inhalt, datei.filename)
    return {"dateiname": datei.filename, "chunks": anzahl}


@app.post("/fragen")
def frage_stellen(body: FrageRequest):
    if not body.frage.strip():
        raise HTTPException(400, "Frage darf nicht leer sein.")
    return fragen(body.frage)


@app.delete("/dokumente")
def dokumente_loeschen():
    kollektion_leeren()
    return {"status": "geleert"}
