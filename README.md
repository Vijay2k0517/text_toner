# Text Toner - Common README

This document describes how the Flutter frontend (Text_toner_Frontend) connects to the FastAPI backend (text_toner_backend), how to configure environments, and how to run the full stack in development and production.

## Architecture Overview
- Frontend: Flutter app located in `Text_toner_Frontend/`
- Backend: FastAPI app with MongoDB located in `text_toner_backend/`
- Communication: HTTP JSON over a single POST endpoint

## API Contract
- Endpoint: `POST /chat`
- Request JSON:
```json
{ "message": "user text here" }
```
- Response JSON:
```json
{ "response": "bot text here" }
```

## Frontend Integration (Flutter)
Key files:
- `lib/config/app_config.dart`: Holds `apiBaseUrl` and `chatEndpointPath`. You can override the base URL at runtime via `--dart-define`.
- `lib/services/api_client.dart`: Uses the Dart `http` package to call the backend `/chat` endpoint.
- `lib/providers/chat_provider.dart`: Sends user messages to the backend, manages typing state, handles errors, and appends bot responses.
- `lib/screens/chat_screen.dart`: Wires the provider to the UI, shows typing indicator, auto-scrolls, and displays SnackBars on errors.

Dart define override example:
- Android emulator: `--dart-define=API_BASE_URL=http://10.0.2.2:8000`
- iOS simulator: `--dart-define=API_BASE_URL=http://127.0.0.1:8000`
- Web/Desktop: `--dart-define=API_BASE_URL=http://localhost:8000`
- Production: `--dart-define=API_BASE_URL=https://api.example.com`

## Backend (FastAPI)
Ensure the backend exposes `POST /chat` and returns a JSON with a `response` key. MongoDB should already be configured. Start the backend on port 8000 for local development.

Example run (from `text_toner_backend/`):
```bash
# Activate venv if needed, then
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running the Frontend
From `Text_toner_Frontend/`:
```bash
flutter pub get

# Android emulator (maps host localhost)
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000

# iOS simulator
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000

# Web (ensure CORS on backend)
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

## CORS (for Web)
When running on web, ensure the FastAPI app is configured with CORS to allow the Flutter web origin. Example FastAPI CORS setup:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8000", "http://localhost:5353", "http://127.0.0.1:8080", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Adjust origins to match your dev server ports.

## Troubleshooting
- 404/405 errors: Verify the backend route is `POST /chat` and that the base URL is correct.
- Network error/timeouts: Confirm the device can reach the host (Android emulator uses `10.0.2.2` for host). Check firewall/antivirus settings on Windows.
- CORS errors (web): Enable CORS in FastAPI and use the correct origin in `allow_origins`.
- Empty responses: Backend must return `{ "response": "..." }`. Any other shape will be treated as an error.
- SSL issues (production): Use `https` for deployed API and ensure valid certificates.

## Production Notes
- Set `API_BASE_URL` via `--dart-define` or CI/CD environment for release builds.
- Consider server-side rate limiting, request logging, and authentication if required.
- Ensure MongoDB indexes/log retention as appropriate.

## Repository Structure (relevant parts)
```
Text_Toner/
├─ text_toner_backend/
│  └─ app/ ... FastAPI code
├─ Text_toner_Frontend/
│  └─ lib/ ... Flutter app
└─ README.md (this file)
```
