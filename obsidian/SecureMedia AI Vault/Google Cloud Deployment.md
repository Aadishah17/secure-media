# Google Cloud Deployment

The app is deployed as a single Google Cloud Run service.

## Live URL

https://securemedia-ai-97902534410.us-central1.run.app

## Deployment Model

- React builds into `dist/`.
- Flask serves the frontend and API.
- Docker packages both into one container.
- Cloud Run hosts the final service.

## Important Files

- `Dockerfile`
- `cloudbuild.yaml`
- `.gcloudignore`
- `scripts/deploy-cloud-run.ps1`
- `docs/google-cloud-deploy.md`

## Deploy Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cloud-run.ps1 -ProjectId collab-learn-6b53c
```

