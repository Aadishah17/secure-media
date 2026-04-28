import base64
import json
from io import BytesIO

from backend.app import create_app


SMALL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def test_upload_requires_file():
    app = create_app()
    client = app.test_client()

    response = client.post("/upload", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.get_json() == {"error": "No image file provided"}


def test_upload_rejects_non_image_file():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/upload",
        data={"file": (BytesIO(b"plain text"), "notes.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Only image uploads are allowed"}


def test_upload_rejects_invalid_image_bytes():
    app = create_app({"HASH_STORE_PATH": "backend/tests/missing-hashes.json"})
    client = app.test_client()

    response = client.post(
        "/upload",
        data={"file": (BytesIO(b"fake image bytes"), "sample.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Uploaded file is not a valid image"}


def test_upload_processes_image_with_securemedia_core(tmp_path):
    app = create_app({"HASH_STORE_PATH": str(tmp_path / "hashes.json")})
    client = app.test_client()

    response = client.post(
        "/upload",
        data={"file": (BytesIO(SMALL_PNG), "sample.png")},
        content_type="multipart/form-data",
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert set(payload) == {
        "hash",
        "similarity",
        "status",
        "best_match",
        "matches",
    }
    assert payload["status"] == "original"
    assert payload["similarity"] == 0.0
    assert payload["best_match"] is None
    assert payload["matches"] == []
    assert isinstance(payload["hash"], str)


def test_upload_marks_matching_stored_hash_as_duplicate(tmp_path):
    hash_store = tmp_path / "hashes.json"
    hash_store.write_text(
        json.dumps([{"id": "stored-sample", "hash": "8000000000000000"}]),
        encoding="utf-8",
    )
    app = create_app({"HASH_STORE_PATH": str(hash_store)})
    client = app.test_client()

    response = client.post(
        "/upload",
        data={"file": (BytesIO(SMALL_PNG), "sample.png")},
        content_type="multipart/form-data",
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "duplicate"
    assert payload["similarity"] == 100.0
    assert payload["best_match"]["id"] == "stored-sample"
    assert payload["matches"][0]["hash"] == "8000000000000000"
