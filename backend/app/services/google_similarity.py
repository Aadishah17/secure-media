from pathlib import Path

from .embedding_store import (
    SimilarityServiceError,
    cosine_similarity,
    load_embedding_store,
    save_embedding_store,
)


class GoogleSimilarityService:
    def __init__(
        self,
        project_id,
        location,
        store_path,
        model_name="multimodalembedding@001",
        dimension=512,
    ):
        if not project_id:
            raise ValueError("Google similarity requires a project_id.")

        self.project_id = project_id
        self.location = location or "us-central1"
        self.store_path = Path(store_path)
        self.model_name = model_name or "multimodalembedding@001"
        self.dimension = int(dimension)
        self._image_class = None
        self._model = None

    def _load_runtime(self):
        if self._image_class is not None and self._model is not None:
            return

        try:
            import vertexai
            from vertexai.vision_models import Image, MultiModalEmbeddingModel
        except ImportError as exc:
            raise SimilarityServiceError(
                "Google Vertex AI similarity runtime is not installed."
            ) from exc

        try:
            vertexai.init(project=self.project_id, location=self.location)
            model = MultiModalEmbeddingModel.from_pretrained(self.model_name)
        except Exception as exc:
            raise SimilarityServiceError(
                "Failed to load Google Vertex AI embedding model."
            ) from exc

        self._image_class = Image
        self._model = model

    def embedding_for_image(self, image_path):
        self._load_runtime()

        try:
            image = self._image_class.load_from_file(str(image_path))
            result = self._model.get_embeddings(image=image, dimension=self.dimension)
            return [float(value) for value in result.image_embedding]
        except Exception as exc:
            raise SimilarityServiceError(
                "Failed to generate Google Vertex AI image embedding."
            ) from exc

    def compare_against_store(self, image_path):
        records = load_embedding_store(self.store_path)
        if not records:
            return {
                "similarity": 0.0,
                "best_match": None,
                "matches": [],
            }

        embedding = self.embedding_for_image(image_path)
        matches = []

        for record in records:
            similarity = cosine_similarity(embedding, record["embedding"])
            matches.append(
                {
                    "id": record["id"],
                    "owner": record["owner"],
                    "similarity": similarity,
                }
            )

        matches.sort(key=lambda item: item["similarity"], reverse=True)
        best_match = matches[0] if matches else None

        return {
            "similarity": best_match["similarity"] if best_match else 0.0,
            "best_match": best_match,
            "matches": matches,
        }

    def store_embedding(self, image_path, item_id, owner="Unverified"):
        embedding = self.embedding_for_image(image_path)
        records = load_embedding_store(self.store_path)
        filtered = [record for record in records if record["id"] != str(item_id)]
        filtered.append(
            {
                "id": str(item_id),
                "owner": str(owner or "Unverified"),
                "embedding": embedding,
            }
        )
        save_embedding_store(self.store_path, filtered)
        return True
