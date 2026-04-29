# Codex Start Here

This note is the short project handoff for future Codex sessions. Read this before doing broad analysis.

## Current Project

SecureMedia AI is a Google Solution Challenge prototype for image originality, duplicate detection, and ownership verification.

Live app: https://securemedia-ai-97902534410.us-central1.run.app

GitHub: https://github.com/Aadishah17/secure-media

Team: double trouble 2x

Members:

- Aadi shah
- nitya singh

## Current State

- Branch: `main`
- Remote: `origin/main`
- Frontend: React and Vite upload UI
- Backend: Flask API with `/upload`, `/api/health`, and frontend serving
- Deployment: Google Cloud Run single-service container
- Presentation assets: PPTX, PDF, and demo video are generated
- Secrets: `backend/.env` is ignored and must not be committed

## Important Commands

Backend tests:

```bash
python -m pytest -q
```

Frontend tests:

```bash
npm test -- --run
```

Frontend build:

```bash
npm run build
```

Local backend:

```bash
python -m flask --app backend.run run --debug
```

Cloud Run deploy:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-cloud-run.ps1 -ProjectId collab-learn-6b53c
```

## File Map

- `src/App.jsx`: React app shell and upload UI integration
- `src/components/`: upload and result UI components
- `backend/app/routes.py`: Flask routes and upload endpoint
- `backend/app/__init__.py`: app config and env loading
- `backend/app/services/integration.py`: combined upload processing pipeline
- `backend/app/services/securemedia_core_adapter.py`: hash-based duplicate workflow
- `backend/app/services/gemini_similarity.py`: Gemini similarity provider
- `backend/app/services/google_similarity.py`: Vertex AI similarity provider
- `backend/app/services/hf_similarity.py`: Hugging Face similarity provider
- `backend/app/services/blockchain_ownership.py`: blockchain ownership service
- `contracts/SecureMediaOwnership.sol`: ownership smart contract
- `docs/SecureMedia_AI_Solution_Challenge_Deck.pptx`: presentation deck
- `docs/SecureMedia_AI_Solution_Challenge_Deck.pdf`: PDF deck
- `docs/video/securemedia-demo.mp4`: demo video

## Upload Pipeline

1. React sends an image file to `/upload`.
2. Flask validates the upload and saves a temporary file.
3. SecureMedia core generates a perceptual hash.
4. Optional AI provider compares embeddings or descriptions.
5. Ownership service attempts blockchain registration and verification.
6. Backend returns similarity, duplicate status, owner, and blockchain verification.

Response shape:

```json
{
  "similarity": 0.0,
  "duplicate": false,
  "owner": "Unverified",
  "blockchain_verified": false
}
```

## Environment Rules

- Never commit `backend/.env`.
- `GEMINI_API_KEY` lives only in ignored local env or Secret Manager.
- Blockchain private keys must never be committed.
- `backend/.env.example` may contain placeholders only.

## Known Risks

- The Gemini API key previously appeared in chat; rotate it before serious production use.
- Live blockchain verification still depends on a valid deployed contract, funded wallet, and real private key.
- Production AI similarity quality depends on persistent stored image data and provider configuration.

## Fast Orientation

For project explanation, read:

- [[Project Overview]]
- [[System Architecture]]
- [[Upload Flow]]
- [[Environment Setup]]

For demo or judging, read:

- [[Demo and Presentation]]
- [[Google Cloud Deployment]]
- [[Screenshots]]
- [[Judge Q&A]]
- [[Remaining Work]]
