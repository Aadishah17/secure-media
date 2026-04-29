# Upload Flow

## Endpoint

- Method: `POST`
- Path: `/upload`
- Field name: `file`
- Accepted input: image file

## Backend Steps

1. Validate that a file exists.
2. Reject non-image uploads.
3. Save the upload temporarily.
4. Run the combined processing service.
5. Delete the temporary file.
6. Return JSON to the frontend.

## Test Request

```bash
curl -X POST https://securemedia-ai-97902534410.us-central1.run.app/upload -F "file=@image.png"
```

## Important Files

- `backend/app/routes.py`
- `backend/app/services/integration.py`
- `backend/app/services/securemedia_core_adapter.py`

