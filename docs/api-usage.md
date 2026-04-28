# SecureMedia API Usage

## Install

Backend core:

```bash
python -m pip install -r backend/requirements.txt
```

Optional AI and blockchain support:

```bash
python -m pip install -r backend/requirements-ai.txt
python -m pip install -r backend/requirements-web3.txt
```

## Run the Flask API

From the repo root:

```bash
python -m flask --app backend.run run --debug
```

The default upload endpoint is:

```text
POST http://127.0.0.1:5000/upload
```

## Example Request

```bash
curl -X POST http://127.0.0.1:5000/upload ^
  -F "file=@C:/path/to/image.png"
```

## Example Response

```json
{
  "similarity": 91.0,
  "duplicate": true,
  "owner": "0xabc123...",
  "blockchain_verified": true
}
```

## Notes

- Hash-based duplicate checks work with the default backend install.
- Hugging Face similarity falls back cleanly when the optional runtime is unavailable.
- Blockchain ownership falls back to the local ownership registry when Web3 config is missing.
