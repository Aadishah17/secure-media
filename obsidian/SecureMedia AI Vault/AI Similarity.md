# AI Similarity

The project supports multiple optional similarity providers. The hash-based path remains the fallback so uploads can still work without external AI credentials.

## Providers

- Gemini: configured with `SIMILARITY_PROVIDER=gemini` and `GEMINI_API_KEY`.
- Hugging Face: configured with `SIMILARITY_PROVIDER=huggingface`.
- Google Vertex AI: configured with `SIMILARITY_PROVIDER=google`.

## Important Files

- `backend/app/services/gemini_similarity.py`
- `backend/app/services/hf_similarity.py`
- `backend/app/services/google_similarity.py`
- `backend/app/services/embedding_store.py`
- `backend/app/services/integration.py`

## Security Note

Never commit `backend/.env`. Store real keys locally or in Google Secret Manager.

