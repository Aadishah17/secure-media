# SecureMedia AI

Minimal SecureMedia AI prototype with:

- Flask backend for image upload and analysis
- React frontend for upload, preview, and results
- Optional Hugging Face image similarity
- Optional Google Vertex AI image similarity
- Optional blockchain ownership verification on EVM testnets

## Structure

```text
backend/
  app/
    routes.py
    services/
  tests/
contracts/
docs/
src/
```

## Run

Frontend:

```bash
npm install
npm run dev
```

Backend:

```bash
python -m pip install -r backend/requirements.txt
python -m flask --app backend.run run --debug
```

Local dev uses the Vite proxy for `/upload` and `/api/health`, so the frontend can talk to Flask without a separate CORS setup.

Optional integrations:

```bash
python -m pip install -r backend/requirements-ai.txt
python -m pip install -r backend/requirements-google.txt
python -m pip install -r backend/requirements-web3.txt
```

Backend environment values can be set through `backend/.env`. Use `backend/.env.example` as the template.

Set `SIMILARITY_PROVIDER=google` to use Vertex AI multimodal embeddings with
`GOOGLE_CLOUD_PROJECT` and local Application Default Credentials.

## Google Cloud deploy

This repo is set up to deploy as a single Cloud Run service:

- Vite builds the frontend into `dist/`
- Flask serves the built frontend and `/upload`
- `Dockerfile` builds both parts into one container

See [docs/google-cloud-deploy.md](</C:/Users/sseja/OneDrive/Documents/New project 2/docs/google-cloud-deploy.md>) for the deploy flow.
