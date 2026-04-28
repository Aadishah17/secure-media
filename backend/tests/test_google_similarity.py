import json

import pytest

from backend.app.services.google_similarity import GoogleSimilarityService


def test_google_similarity_uses_best_match_from_store(tmp_path, monkeypatch):
    store_path = tmp_path / "google-embeddings.json"
    store_path.write_text(
        json.dumps(
            [
                {"id": "stored-a", "owner": "Owner A", "embedding": [1.0, 0.0]},
                {"id": "stored-b", "owner": "Owner B", "embedding": [0.0, 1.0]},
            ]
        ),
        encoding="utf-8",
    )

    service = GoogleSimilarityService(
        project_id="demo-project",
        location="us-central1",
        store_path=store_path,
    )
    monkeypatch.setattr(
        service,
        "embedding_for_image",
        lambda image_path: [1.0, 0.0],
    )

    result = service.compare_against_store(tmp_path / "sample.png")

    assert result == {
        "similarity": 100.0,
        "best_match": {
            "id": "stored-a",
            "owner": "Owner A",
            "similarity": 100.0,
        },
        "matches": [
            {"id": "stored-a", "owner": "Owner A", "similarity": 100.0},
            {"id": "stored-b", "owner": "Owner B", "similarity": 0.0},
        ],
    }


def test_google_similarity_persists_generated_embeddings(tmp_path, monkeypatch):
    store_path = tmp_path / "google-embeddings.json"
    service = GoogleSimilarityService(
        project_id="demo-project",
        location="us-central1",
        store_path=store_path,
    )
    monkeypatch.setattr(
        service,
        "embedding_for_image",
        lambda image_path: [0.25, 0.75],
    )

    service.store_embedding(tmp_path / "sample.png", "hash-a", owner="0xowner")

    assert json.loads(store_path.read_text(encoding="utf-8")) == [
        {"id": "hash-a", "owner": "0xowner", "embedding": [0.25, 0.75]}
    ]


def test_google_similarity_requires_project_id(tmp_path):
    with pytest.raises(ValueError, match="project_id"):
        GoogleSimilarityService(project_id="", location="us-central1", store_path=tmp_path / "store.json")
