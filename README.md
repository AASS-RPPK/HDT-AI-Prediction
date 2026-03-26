# HDT AI Prediction (FastAPI)

This service implements asynchronous annotation prediction endpoints.

From your screenshot ("AI Prediction Actions"), the intent is:

- `POST /models/annotation`
- `GET /models/annotation`

In the current codebase, the implemented and gateway-routed paths are:

- `POST /model/annotations`
- `GET /model/annotations`

These are exposed through `HDT-API-Gateway` via `/model/annotations`.

## Run

1. Install dependencies
   - `pip install -r requirements.txt`
2. Start the API server
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Endpoints

### Start AI predicting process

`POST /model/annotations`

Body (JSON):
```json
{
  "image_id": "image-123",
  "model_version": "latest"
}
```

Behavior:
- Creates a prediction task and returns immediately (`202 Accepted`).
- Processing is asynchronous (Celery worker).

### Retrieve finished AI prediction

`GET /model/annotations`

Query params:
- `image_id` (optional)
- `state` (optional)
- `limit` (optional, default `50`)
- `offset` (optional, default `0`)

