# SecureMedia AI

Minimal SecureMedia AI prototype with:

- Flask backend for image upload and analysis
- React frontend for upload, preview, and results
- Optional Hugging Face image similarity
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

Optional integrations:

```bash
python -m pip install -r backend/requirements-ai.txt
python -m pip install -r backend/requirements-web3.txt
```

Backend environment values can be set through `backend/.env`. Use `backend/.env.example` as the template.
