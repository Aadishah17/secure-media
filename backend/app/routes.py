from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)


@upload_bp.post("/upload")
def upload_image():
    uploaded_file = request.files.get("file")

    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({"error": "No image file provided"}), 400

    if not uploaded_file.mimetype.startswith("image/"):
        return jsonify({"error": "Only image uploads are allowed"}), 400

    payload = uploaded_file.read()

    return jsonify(
        {
            "message": "Image uploaded successfully",
            "filename": secure_filename(uploaded_file.filename),
            "content_type": uploaded_file.mimetype,
            "size": len(payload),
        }
    )
