from .blockchain_ownership import BlockchainOwnershipService
from .google_similarity import GoogleSimilarityService
from .hf_similarity import HuggingFaceSimilarityService
from .securemedia_core_adapter import analyze_with_securemedia_core, store_original_hash


class HashingService:
    def __init__(self, hash_store_path, threshold, hash_size):
        self.hash_store_path = hash_store_path
        self.threshold = threshold
        self.hash_size = hash_size

    def analyze_image(self, image_path):
        return analyze_with_securemedia_core(
            image_path,
            self.hash_store_path,
            threshold=self.threshold,
            hash_size=self.hash_size,
        )

    def store_original_hash(self, image_path, image_hash):
        return store_original_hash(image_path, self.hash_store_path, image_hash)


class CombinedProcessingService:
    def __init__(
        self,
        hash_service,
        similarity_service,
        ownership_service,
        duplicate_threshold,
    ):
        self.hash_service = hash_service
        self.similarity_service = similarity_service
        self.ownership_service = ownership_service
        self.duplicate_threshold = duplicate_threshold

    @classmethod
    def from_config(cls, config):
        similarity_provider = str(config.get("SIMILARITY_PROVIDER", "huggingface")).lower()
        if similarity_provider == "google":
            similarity_service = GoogleSimilarityService(
                project_id=config.get("GOOGLE_CLOUD_PROJECT"),
                location=config.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
                store_path=config.get("GOOGLE_EMBEDDING_STORE_PATH"),
                model_name=config.get("GOOGLE_MODEL_NAME", "multimodalembedding@001"),
                dimension=config.get("GOOGLE_EMBEDDING_DIMENSION", 512),
            )
        else:
            similarity_service = HuggingFaceSimilarityService(
                model_name=config["HF_MODEL_NAME"],
                store_path=config["EMBEDDING_STORE_PATH"],
            )

        return cls(
            hash_service=HashingService(
                hash_store_path=config["HASH_STORE_PATH"],
                threshold=config["DUPLICATE_THRESHOLD"],
                hash_size=config["HASH_SIZE"],
            ),
            similarity_service=similarity_service,
            ownership_service=BlockchainOwnershipService(
                provider_uri=config.get("WEB3_PROVIDER_URI"),
                contract_address=config.get("CONTRACT_ADDRESS"),
                owner_address=config.get("OWNER_ADDRESS"),
                private_key=config.get("PRIVATE_KEY"),
                chain_id=config.get("CHAIN_ID"),
                registry_path=config["OWNERSHIP_STORE_PATH"],
            ),
            duplicate_threshold=config["DUPLICATE_THRESHOLD"],
        )

    def process_upload(self, image_path):
        hash_result = self.hash_service.analyze_image(image_path)

        similarity = float(hash_result["similarity"])
        duplicate = hash_result["status"] == "duplicate"
        ai_result = None

        try:
            ai_result = self.similarity_service.compare_against_store(image_path)
            if ai_result.get("best_match") is not None:
                similarity = float(ai_result["similarity"])
                duplicate = similarity >= self.duplicate_threshold
        except Exception:
            pass

        image_hash = hash_result["hash"]
        try:
            self.ownership_service.register_hash(image_hash)
        except Exception:
            pass

        try:
            ownership = self.ownership_service.verify_hash(image_hash)
        except Exception:
            ownership = {"owner": "Unverified", "blockchain_verified": False}

        owner = ownership.get("owner", "Unverified") or "Unverified"
        if owner == "Unverified" and ai_result and ai_result.get("best_match"):
            owner = ai_result["best_match"].get("owner", owner) or owner

        if not duplicate:
            try:
                self.hash_service.store_original_hash(image_path, image_hash)
            except Exception:
                pass

            try:
                self.similarity_service.store_embedding(image_path, image_hash, owner)
            except Exception:
                pass

        return {
            "similarity": round(similarity, 2),
            "duplicate": bool(duplicate),
            "owner": owner,
            "blockchain_verified": bool(ownership.get("blockchain_verified", False)),
        }
