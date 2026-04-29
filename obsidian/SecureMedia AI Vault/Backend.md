# Backend

The backend is a Flask application that accepts image uploads and coordinates all processing modules.

## Key Routes

- `/` serves the built frontend.
- `/api/health` returns service health.
- `/healthz` returns service health.
- `/upload` processes uploaded images.

## Important Files

- `backend/app/__init__.py`
- `backend/app/routes.py`
- `backend/run.py`
- `backend/tests/`

## Local Run

```bash
python -m pip install -r backend/requirements.txt
python -m flask --app backend.run run --debug
```

## Verification

```bash
python -m pytest -q
```

