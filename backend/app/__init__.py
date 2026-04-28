from flask import Flask

from .routes import upload_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        HASH_STORE_PATH="backend/data/hashes.json",
        EMBEDDING_STORE_PATH="backend/data/embeddings.json",
        OWNERSHIP_STORE_PATH="backend/data/ownership.json",
        DUPLICATE_THRESHOLD=90.0,
        HASH_SIZE=8,
        HF_MODEL_NAME="openai/clip-vit-base-patch32",
        WEB3_PROVIDER_URI=None,
        CONTRACT_ADDRESS=None,
        OWNER_ADDRESS=None,
        PRIVATE_KEY=None,
        CHAIN_ID=None,
        UPLOAD_PROCESSOR=None,
    )

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(upload_bp)
    return app
