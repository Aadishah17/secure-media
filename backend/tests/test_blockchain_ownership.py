import json

from backend.app.services.blockchain_ownership import BlockchainOwnershipService


def test_registry_fallback_registers_and_verifies_hash(tmp_path):
    registry_path = tmp_path / "ownership.json"
    service = BlockchainOwnershipService(
        owner_address="0xabc123",
        registry_path=registry_path,
    )

    service.register_hash("hash-1")

    stored = json.loads(registry_path.read_text(encoding="utf-8"))
    assert stored["hash-1"]["owner"] == "0xabc123"
    assert service.verify_hash("hash-1") == {
        "owner": "0xabc123",
        "blockchain_verified": False,
    }
    assert service.verify_claimant("hash-1", "0xabc123") is True
    assert service.verify_claimant("hash-1", "0xdef456") is False
