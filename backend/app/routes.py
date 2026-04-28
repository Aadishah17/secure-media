import os
import tempfile
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from .services.integration import CombinedProcessingService
from .services.media_check import InvalidImageError

upload_bp = Blueprint("upload", __name__)


@upload_bp.get("/healthz")
@upload_bp.get("/api/health")
def healthcheck():
    return jsonify({"status": "ok"})


def _frontend_dist_path():
    return Path(current_app.config["FRONTEND_DIST_PATH"])


@upload_bp.get("/")
def serve_index():
    dist_path = _frontend_dist_path()
    index_path = dist_path / "index.html"
    if not index_path.exists():
        return jsonify({"error": "Frontend build not found"}), 404
    return send_from_directory(dist_path, "index.html")


@upload_bp.get("/<path:asset_path>")
def serve_frontend_asset(asset_path):
    dist_path = _frontend_dist_path()
    requested_path = dist_path / asset_path
    if requested_path.exists() and requested_path.is_file():
        return send_from_directory(dist_path, asset_path)

    index_path = dist_path / "index.html"
    if index_path.exists():
        return send_from_directory(dist_path, "index.html")

    return jsonify({"error": "Frontend build not found"}), 404


@upload_bp.post("/upload")
def upload_image():
    uploaded_file = request.files.get("file")

    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({"error": "No image file provided"}), 400

    if not uploaded_file.mimetype.startswith("image/"):
        return jsonify({"error": "Only image uploads are allowed"}), 400

    suffix = Path(secure_filename(uploaded_file.filename)).suffix or ".upload"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = temp_file.name
    temp_file.close()

    try:
        uploaded_file.save(temp_path)
        processor = current_app.config.get("UPLOAD_PROCESSOR")
        if processor is None:
            processor = CombinedProcessingService.from_config(current_app.config)
        result = processor.process_upload(temp_path)
    except InvalidImageError:
        return jsonify({"error": "Uploaded file is not a valid image"}), 400
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify(result)
