from io import BytesIO

from backend.app import create_app


def test_upload_requires_file():
    app = create_app()
    client = app.test_client()

    response = client.post("/upload", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.get_json() == {"error": "No image file provided"}


def test_upload_rejects_non_image_file():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/upload",
        data={"file": (BytesIO(b"plain text"), "notes.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Only image uploads are allowed"}


def test_upload_accepts_image_file():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/upload",
        data={"file": (BytesIO(b"fake image bytes"), "sample.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Image uploaded successfully",
        "filename": "sample.png",
        "content_type": "image/png",
        "size": 16,
    }
