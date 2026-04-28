import importlib.util
import os
from functools import lru_cache
from pathlib import Path

from PIL import UnidentifiedImageError

from .media_check import InvalidImageError
from .media_check import add_original_hash as local_add_original_hash
from .media_check import analyze_image as local_analyze_image


def _securemedia_core_path():
    codex_home = os.environ.get("CODEX_HOME")
    roots = []

    if codex_home:
        roots.append(Path(codex_home))

    roots.append(Path.home() / ".codex")

    for root in roots:
        candidate = root / "skills" / "securemedia-core" / "scripts" / "securemedia_compare.py"
        if candidate.exists():
            return candidate

    return None


@lru_cache(maxsize=1)
def _load_securemedia_core_module():
    script_path = _securemedia_core_path()
    if script_path is None:
        return None

    spec = importlib.util.spec_from_file_location("securemedia_core_script", script_path)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_securemedia_core_analyzer():
    module = _load_securemedia_core_module()
    if module is None:
        return None
    return getattr(module, "analyze_image", None)


def analyze_with_securemedia_core(image_path, hash_store_path, threshold=90.0, hash_size=8):
    analyzer = _load_securemedia_core_analyzer()
    if analyzer is None:
        return local_analyze_image(image_path, hash_store_path, threshold=threshold, hash_size=hash_size)

    try:
        return analyzer(
            Path(image_path),
            Path(hash_store_path),
            threshold=threshold,
            hash_size=hash_size,
        )
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("Uploaded file is not a valid image") from exc


def store_original_hash(image_path, hash_store_path, image_hash):
    module = _load_securemedia_core_module()
    item_id = Path(image_path).stem or "upload"

    if module is None:
        return local_add_original_hash(hash_store_path, image_hash, item_id)

    load_store = getattr(module, "load_store", None)
    save_store = getattr(module, "save_store", None)
    if load_store is None or save_store is None:
        return local_add_original_hash(hash_store_path, image_hash, item_id)

    store_path = Path(hash_store_path)
    entries = load_store(store_path)
    if any(entry.get("hash") == image_hash for entry in entries):
        return False

    entries.append({"id": item_id, "hash": str(image_hash)})
    save_store(store_path, entries)
    return True
