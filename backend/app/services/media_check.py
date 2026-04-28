import json
from pathlib import Path

from PIL import Image, UnidentifiedImageError
import imagehash


class InvalidImageError(ValueError):
    pass


def load_store(path):
    hash_store = Path(path)
    if not hash_store.exists():
        return []

    data = json.loads(hash_store.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("hashes"), list):
        data = data["hashes"]
    elif isinstance(data, dict):
        data = [{"id": str(key), "hash": str(value)} for key, value in data.items()]

    if not isinstance(data, list):
        raise ValueError("Hash store must be a list, a {'hashes': [...]} object, or an id/hash map.")

    entries = []
    for index, item in enumerate(data):
        if isinstance(item, str):
            entries.append({"id": str(index), "hash": item})
        elif isinstance(item, dict) and item.get("hash"):
            entries.append(
                {
                    "id": str(item.get("id", index)),
                    "hash": str(item["hash"]),
                }
            )

    return entries


def save_store(path, entries):
    hash_store = Path(path)
    hash_store.parent.mkdir(parents=True, exist_ok=True)
    hash_store.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def add_original_hash(path, image_hash, item_id):
    entries = load_store(path)
    if any(entry.get("hash") == image_hash for entry in entries):
        return False

    entries.append({"id": str(item_id), "hash": str(image_hash)})
    save_store(path, entries)
    return True


def phash_image(image_path, hash_size):
    try:
        with Image.open(image_path) as image:
            return imagehash.phash(image, hash_size=hash_size)
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("Uploaded file is not a valid image") from exc


def compare_hashes(current_hash, entries):
    matches = []
    max_bits = current_hash.hash.size

    for entry in entries:
        try:
            stored_hash = imagehash.hex_to_hash(entry["hash"])
            distance = current_hash - stored_hash
        except Exception:
            continue

        similarity = max(0.0, (1.0 - (distance / max_bits)) * 100.0)
        matches.append(
            {
                "id": entry["id"],
                "hash": entry["hash"],
                "distance": int(distance),
                "similarity": round(similarity, 2),
            }
        )

    return sorted(matches, key=lambda item: item["similarity"], reverse=True)


def analyze_image(image_path, hash_store_path, threshold=90.0, hash_size=8):
    current_hash = phash_image(Path(image_path), hash_size=hash_size)
    matches = compare_hashes(current_hash, load_store(hash_store_path))
    best_match = matches[0] if matches else None
    similarity = best_match["similarity"] if best_match else 0.0

    return {
        "hash": str(current_hash),
        "similarity": similarity,
        "status": "duplicate" if best_match and similarity >= threshold else "original",
        "best_match": best_match,
        "matches": matches,
    }
