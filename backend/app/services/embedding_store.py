import json
from math import sqrt
from pathlib import Path


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
