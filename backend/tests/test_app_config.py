import os
from pathlib import Path

from backend.app import create_app


def test_create_app_reads_backend_dotenv_and_process_env(monkeypatch):
    env_path = Path("backend/.env")
    original_text = env_path.read_text(encoding="utf-8") if env_path.exists() else None

    env_path.write_text(
        "\n".join(
            [
                "WEB3_PROVIDER_URI=https://example-rpc.test",
                "CONTRACT_ADDRESS=0xFromDotEnv",
                "OWNER_ADDRESS=0xOwnerFromDotEnv",
                "CHAIN_ID=11155111",
                "SIMILARITY_PROVIDER=gemini",
                "GEMINI_API_KEY=gemini-test-key",
                "GOOGLE_CLOUD_PROJECT=securemedia-demo",
                "GOOGLE_CLOUD_LOCATION=europe-west4",
                "GOOGLE_MODEL_NAME=multimodalembedding@001",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("CONTRACT_ADDRESS", "0xFromProcessEnv")

    try:
        app = create_app()
    finally:
        if original_text is None:
            env_path.unlink(missing_ok=True)
        else:
            env_path.write_text(original_text, encoding="utf-8")

    assert app.config["WEB3_PROVIDER_URI"] == "https://example-rpc.test"
    assert app.config["CONTRACT_ADDRESS"] == "0xFromProcessEnv"
    assert app.config["OWNER_ADDRESS"] == "0xOwnerFromDotEnv"
    assert app.config["CHAIN_ID"] == 11155111
    assert app.config["SIMILARITY_PROVIDER"] == "gemini"
    assert app.config["GEMINI_API_KEY"] == "gemini-test-key"
    assert app.config["GOOGLE_CLOUD_PROJECT"] == "securemedia-demo"
    assert app.config["GOOGLE_CLOUD_LOCATION"] == "europe-west4"
    assert app.config["GOOGLE_MODEL_NAME"] == "multimodalembedding@001"
