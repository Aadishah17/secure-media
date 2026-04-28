import json
from math import sqrt
from pathlib import Path

from PIL import Image


class SimilarityServiceError(RuntimeError):
    pass


def load_embedding_store(path):
    store_path = Path(path)
    if not store_path.exists():
        return []

    data = json.loads(store_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Embedding store must be a list of embedding records.")

    records = []
    for item in data:
        if not isinstance(item, dict):
            continue
        embedding = item.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            continue
        records.append(
            {
                "id": str(item.get("id", "unknown")),
                "owner": str(item.get("owner", "Unverified")),
                "embedding": [float(value) for value in embedding],
            }
        )

    return records


def save_embedding_store(path, records):
    store_path = Path(path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def cosine_similarity(left, right):
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = sqrt(sum(a * a for a in left))
    right_norm = sqrt(sum(b * b for b in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    score = numerator / (left_norm * right_norm)
    return max(0.0, round(score * 100.0, 2))


class HuggingFaceSimilarityService:
    def __init__(self, model_name, store_path):
        self.model_name = model_name
        self.store_path = Path(store_path)
        self._processor = None
        self._model = None
        self._torch = None

    def _load_runtime(self):
        if self._processor is not None and self._model is not None and self._torch is not None:
            return

        try:
            import torch
            from transformers import AutoImageProcessor, AutoModel
        except ImportError as exc:
            raise SimilarityServiceError(
                "Hugging Face similarity runtime is not installed."
            ) from exc

        try:
            processor = AutoImageProcessor.from_pretrained(self.model_name)
            model = AutoModel.from_pretrained(self.model_name)
            model.eval()
        except Exception as exc:
            raise SimilarityServiceError("Failed to load Hugging Face image model.") from exc

        self._torch = torch
        self._processor = processor
        self._model = model

    def embedding_for_image(self, image_path):
        self._load_runtime()

        try:
            with Image.open(image_path) as image:
                rgb_image = image.convert("RGB")

            inputs = self._processor(images=rgb_image, return_tensors="pt")
            with self._torch.no_grad():
                outputs = self._model(**inputs)
            vector = outputs.pooler_output[0]
            vector = vector / vector.norm(p=2)
            return vector.cpu().tolist()
        except Exception as exc:
            raise SimilarityServiceError("Failed to generate image embedding.") from exc

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
