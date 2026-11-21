import os, sys
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))
from main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_frage_leer_gibt_400():
    assert client.post("/fragen", json={"frage": "  "}).status_code == 400


def test_frage_ohne_body_gibt_422():
    assert client.post("/fragen", json={}).status_code == 422


def test_dokument_falscher_typ():
    res = client.post("/dokument", files={"datei": ("test.exe", b"data", "application/octet-stream")})
    assert res.status_code == 400


def test_fragen_ohne_dokument():
    with patch("main.fragen", return_value={"antwort": "Bitte zuerst ein Dokument hochladen.", "quellen": []}):
        res = client.post("/fragen", json={"frage": "Was steht drin?"})
    assert res.status_code == 200
    assert "quellen" in res.json()


def test_dokument_hochladen_mock():
    with patch("main.dokument_laden", return_value=5):
        res = client.post("/dokument", files={"datei": ("test.txt", b"Testinhalt " * 50, "text/plain")})
    assert res.status_code == 200
    assert res.json()["chunks"] == 5


def test_fragen_mit_antwort():
    mock_result = {"antwort": "Die Antwort ist 42.", "quellen": ["doc.pdf"]}
    with patch("main.fragen", return_value=mock_result):
        res = client.post("/fragen", json={"frage": "Was ist die Antwort?"})
    assert res.status_code == 200
    assert res.json()["antwort"] == "Die Antwort ist 42."


def test_dokumente_loeschen():
    with patch("main.kollektion_leeren"):
        res = client.delete("/dokumente")
    assert res.status_code == 200
    assert res.json()["status"] == "geleert"
