import os
from pathlib import Path

from flask import Flask

from .routes import upload_bp


def _load_backend_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return {}

    values = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _env_value(file_values, key, default=None, caster=None):
    raw_value = os.environ.get(key, file_values.get(key, default))
    if raw_value in (None, ""):
        return default
    if caster is None:
        return raw_value
    return caster(raw_value)


def create_app(test_config=None):
    file_env = _load_backend_env()
    app = Flask(__name__)
    app.config.from_mapping(
        HASH_STORE_PATH=_env_value(file_env, "HASH_STORE_PATH", "backend/data/hashes.json"),
        EMBEDDING_STORE_PATH=_env_value(file_env, "EMBEDDING_STORE_PATH", "backend/data/embeddings.json"),
        OWNERSHIP_STORE_PATH=_env_value(file_env, "OWNERSHIP_STORE_PATH", "backend/data/ownership.json"),
        DUPLICATE_THRESHOLD=_env_value(file_env, "DUPLICATE_THRESHOLD", 90.0, float),
        HASH_SIZE=_env_value(file_env, "HASH_SIZE", 8, int),
        HF_MODEL_NAME=_env_value(file_env, "HF_MODEL_NAME", "openai/clip-vit-base-patch32"),
        WEB3_PROVIDER_URI=_env_value(file_env, "WEB3_PROVIDER_URI"),
        CONTRACT_ADDRESS=_env_value(file_env, "CONTRACT_ADDRESS"),
        OWNER_ADDRESS=_env_value(file_env, "OWNER_ADDRESS"),
        PRIVATE_KEY=_env_value(file_env, "PRIVATE_KEY"),
        CHAIN_ID=_env_value(file_env, "CHAIN_ID", None, int),
        UPLOAD_PROCESSOR=None,
    )

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(upload_bp)
    return app
