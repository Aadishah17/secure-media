from pathlib import Path

from backend.app.services.integration import CombinedProcessingService


class StubHashService:
    def __init__(self, payload):
        self.payload = payload
        self.stored_hashes = []

    def analyze_image(self, image_path):
        return self.payload

    def store_original_hash(self, image_path, image_hash):
        self.stored_hashes.append((str(image_path), image_hash))
        return True


class StubSimilarityService:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error
        self.stored_embeddings = []

    def compare_against_store(self, image_path):
        if self.error:
            raise self.error
        return self.payload

    def store_embedding(self, image_path, item_id, owner="Unverified"):
        self.stored_embeddings.append((str(image_path), item_id, owner))
        return True


class StubOwnershipService:
    def __init__(self, payload):
        self.payload = payload
        self.registered_hashes = []

    def register_hash(self, image_hash):
        self.registered_hashes.append(image_hash)

    def verify_hash(self, image_hash):
        return self.payload


class FakeGoogleSimilarityService:
    def __init__(self, project_id, location, store_path, model_name, dimension):
        self.project_id = project_id
        self.location = location
        self.store_path = store_path
        self.model_name = model_name
        self.dimension = dimension


def test_integration_uses_ai_similarity_when_available(tmp_path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"content")
    hash_service = StubHashService({"hash": "hash-a", "similarity": 12.5, "status": "original"})
    similarity_service = StubSimilarityService({"similarity": 91.0, "best_match": {"id": "sample-owner"}})

    service = CombinedProcessingService(
        hash_service=hash_service,
        similarity_service=similarity_service,
        ownership_service=StubOwnershipService({"owner": "0xabc", "blockchain_verified": True}),
        duplicate_threshold=90.0,
    )

    payload = service.process_upload(image_path)

    assert payload == {
        "similarity": 91.0,
        "duplicate": True,
        "owner": "0xabc",
        "blockchain_verified": True,
    }
    assert hash_service.stored_hashes == []
    assert similarity_service.stored_embeddings == []


def test_integration_falls_back_to_hash_similarity_when_ai_fails(tmp_path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"content")
    ownership = StubOwnershipService({"owner": "Unverified", "blockchain_verified": False})
    hash_service = StubHashService({"hash": "hash-b", "similarity": 84.0, "status": "duplicate"})
    similarity_service = StubSimilarityService(error=RuntimeError("model unavailable"))

    service = CombinedProcessingService(
        hash_service=hash_service,
        similarity_service=similarity_service,
        ownership_service=ownership,
        duplicate_threshold=90.0,
    )

    payload = service.process_upload(image_path)

    assert payload == {
        "similarity": 84.0,
        "duplicate": True,
        "owner": "Unverified",
        "blockchain_verified": False,
    }
    assert ownership.registered_hashes == ["hash-b"]
    assert hash_service.stored_hashes == []
    assert similarity_service.stored_embeddings == []


def test_integration_persists_new_originals_for_future_checks(tmp_path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"content")
    hash_service = StubHashService({"hash": "hash-c", "similarity": 0.0, "status": "original"})
    similarity_service = StubSimilarityService({"similarity": 0.0, "best_match": None})

    service = CombinedProcessingService(
        hash_service=hash_service,
        similarity_service=similarity_service,
        ownership_service=StubOwnershipService({"owner": "0xowner", "blockchain_verified": False}),
        duplicate_threshold=90.0,
    )

    payload = service.process_upload(image_path)

    assert payload == {
        "similarity": 0.0,
        "duplicate": False,
        "owner": "0xowner",
        "blockchain_verified": False,
    }
    assert hash_service.stored_hashes == [(str(image_path), "hash-c")]
    assert similarity_service.stored_embeddings == [(str(image_path), "hash-c", "0xowner")]


def test_from_config_builds_google_similarity_service_when_selected(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "backend.app.services.integration.GoogleSimilarityService",
        FakeGoogleSimilarityService,
    )

    service = CombinedProcessingService.from_config(
        {
            "HASH_STORE_PATH": str(tmp_path / "hashes.json"),
            "DUPLICATE_THRESHOLD": 90.0,
            "HASH_SIZE": 8,
            "SIMILARITY_PROVIDER": "google",
            "GOOGLE_CLOUD_PROJECT": "securemedia-demo",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
            "GOOGLE_MODEL_NAME": "multimodalembedding@001",
            "GOOGLE_EMBEDDING_STORE_PATH": str(tmp_path / "google-embeddings.json"),
            "HF_MODEL_NAME": "openai/clip-vit-base-patch32",
            "EMBEDDING_STORE_PATH": str(tmp_path / "hf-embeddings.json"),
            "WEB3_PROVIDER_URI": None,
            "CONTRACT_ADDRESS": None,
            "OWNER_ADDRESS": None,
            "PRIVATE_KEY": None,
            "CHAIN_ID": None,
            "OWNERSHIP_STORE_PATH": str(tmp_path / "ownership.json"),
        }
    )

    assert isinstance(service.similarity_service, FakeGoogleSimilarityService)
    assert service.similarity_service.project_id == "securemedia-demo"
    assert service.similarity_service.location == "us-central1"
    assert str(service.similarity_service.store_path).endswith("google-embeddings.json")
    assert service.similarity_service.model_name == "multimodalembedding@001"
    assert service.similarity_service.dimension == 512
