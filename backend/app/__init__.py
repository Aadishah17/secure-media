from flask import Flask

from .routes import upload_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        HASH_STORE_PATH="backend/data/hashes.json",
        DUPLICATE_THRESHOLD=90.0,
        HASH_SIZE=8,
    )

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(upload_bp)
    return app
