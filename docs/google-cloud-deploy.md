# Google Cloud Deploy

This project is set up for a single-service deploy to Google Cloud Run.

## Architecture

- React is built with Vite into `dist/`
- Flask serves the built frontend and the `/upload` API
- Cloud Run hosts one container for both UI and API

This keeps the deploy simple and avoids frontend/backend CORS issues.

## Prerequisites

Install the Google Cloud CLI and authenticate:

```bash
gcloud auth login
gcloud auth application-default login
```

Set your project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Enable required APIs:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com
```

## Required environment

At minimum, set these for the Cloud Run service:

- `SIMILARITY_PROVIDER=google`
- `GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID`
- `GOOGLE_CLOUD_LOCATION=us-central1`

Optional blockchain variables:

- `WEB3_PROVIDER_URI`
- `CONTRACT_ADDRESS`
- `OWNER_ADDRESS`
- `PRIVATE_KEY`
- `CHAIN_ID`

## One-command source deploy

Google Cloud documents `gcloud run deploy --source .` as the source deployment flow for Cloud Run, and Cloud Run uses your `Dockerfile` when present.

```bash
gcloud run deploy securemedia-ai ^
  --source . ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --set-env-vars SIMILARITY_PROVIDER=google,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1
```

## Deploy helper script

This repo includes a PowerShell helper:

```bash
powershell -ExecutionPolicy Bypass -File scripts/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID
```

Dry-run the generated command first:

```bash
powershell -ExecutionPolicy Bypass -File scripts/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -DryRun
```

If you want Cloud Run to receive secrets instead of plain env vars:

```bash
powershell -ExecutionPolicy Bypass -File scripts/deploy-cloud-run.ps1 ^
  -ProjectId YOUR_PROJECT_ID ^
  -GeminiApiSecretName gemini-api-key ^
  -BlockchainPrivateKeySecretName securemedia-private-key
```

## Cloud Build deploy

This repo also includes `cloudbuild.yaml`:

```bash
gcloud builds submit --config cloudbuild.yaml
```

## After deploy

Check the health endpoint:

```bash
curl https://YOUR_CLOUD_RUN_URL/api/health
```

The frontend loads from the same base URL, and uploads go to:

```text
https://YOUR_CLOUD_RUN_URL/upload
```

## Notes

- For live Vertex AI embeddings, the Cloud Run service account needs access to Vertex AI in your project.
- The Cloud Run deploy supports `--set-secrets`; use that for `GEMINI_API_KEY` and blockchain private keys instead of putting them in `backend/.env`.
- For local development, Vite proxies `/upload` and `/api/health` to Flask.
