# Environment Setup

Use `backend/.env` for local secrets and runtime configuration. This file is ignored by Git and must not be committed.

## Local File

Path:

```text
backend/.env
```

## Current Expected Keys

```env
SIMILARITY_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
HF_MODEL_NAME=openai/clip-vit-base-patch32
WEB3_PROVIDER_URI=your_rpc_url
CONTRACT_ADDRESS=your_deployed_contract_address
OWNER_ADDRESS=your_wallet_address
PRIVATE_KEY=your_wallet_private_key
CHAIN_ID=11155111
```

## Provider Options

- `SIMILARITY_PROVIDER=gemini` uses Gemini similarity.
- `SIMILARITY_PROVIDER=huggingface` uses local Hugging Face similarity if dependencies are installed.
- `SIMILARITY_PROVIDER=google` uses Google Vertex AI similarity if Google Cloud auth is configured.

## Secret Rules

- Never paste real keys into Markdown notes.
- Never commit `backend/.env`.
- Use `backend/.env.example` for placeholders only.
- Use Google Secret Manager for production secrets.

## Verification

Check that the file is ignored:

```bash
git check-ignore -v backend/.env
```

Check that no real env file is tracked:

```bash
git ls-files | findstr /R "\\.env$ backend/.env$"
```
