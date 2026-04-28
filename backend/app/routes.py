import os
import tempfile
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from .services.integration import CombinedProcessingService
from .services.media_check import InvalidImageError

upload_bp = Blueprint("upload", __name__)


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
