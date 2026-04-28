from pathlib import Path

from backend.app.services.integration import CombinedProcessingService


class StubHashService:
    def __init__(self, payload):
        self.payload = payload

    def analyze_image(self, image_path):
        return self.payload


class StubSimilarityService:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def compare_against_store(self, image_path):
        if self.error:
            raise self.error
        return self.payload


class StubOwnershipService:
    def __init__(self, payload):
        self.payload = payload
        self.registered_hashes = []

    def register_hash(self, image_hash):
        self.registered_hashes.append(image_hash)

    def verify_hash(self, image_hash):
        return self.payload


def test_integration_uses_ai_similarity_when_available(tmp_path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"content")

    service = CombinedProcessingService(
        hash_service=StubHashService({"hash": "hash-a", "similarity": 12.5, "status": "original"}),
        similarity_service=StubSimilarityService(
            {"similarity": 91.0, "best_match": {"id": "sample-owner"}}
        ),
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


def test_integration_falls_back_to_hash_similarity_when_ai_fails(tmp_path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"content")
    ownership = StubOwnershipService({"owner": "Unverified", "blockchain_verified": False})

    service = CombinedProcessingService(
        hash_service=StubHashService({"hash": "hash-b", "similarity": 84.0, "status": "duplicate"}),
        similarity_service=StubSimilarityService(error=RuntimeError("model unavailable")),
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
