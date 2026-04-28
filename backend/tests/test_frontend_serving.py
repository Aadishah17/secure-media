from pathlib import Path

from backend.app import create_app


def test_root_serves_built_frontend_index(tmp_path):
    dist_path = tmp_path / "dist"
    dist_path.mkdir()
    index_path = dist_path / "index.html"
    index_path.write_text("<html><body>SecureMedia Cloud Run</body></html>", encoding="utf-8")

    app = create_app({"FRONTEND_DIST_PATH": str(dist_path)})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"SecureMedia Cloud Run" in response.data


def test_unknown_route_falls_back_to_frontend_index(tmp_path):
    dist_path = tmp_path / "dist"
    dist_path.mkdir()
    index_path = dist_path / "index.html"
    index_path.write_text("<html><body>SPA shell</body></html>", encoding="utf-8")

    app = create_app({"FRONTEND_DIST_PATH": str(dist_path)})
    client = app.test_client()

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"SPA shell" in response.data


def test_healthcheck_returns_ok():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
