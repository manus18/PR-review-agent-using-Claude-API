# PR Review Agent

A FastAPI service that reviews code using Anthropic Claude.

## Features

- `POST /review`: submit code for a structured review
- `GET /health`: simple health check
- `GET /docs`: interactive OpenAPI documentation

## Requirements

- Python 3.10+ (project uses `python310` in the local environment)
- `ANTHROPIC_API_KEY` environment variable

## Setup

1. Create and activate the virtual environment

```powershell
cd "C:\Users\manub\OneDrive\Claude"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Copy or populate `.env`

```powershell
copy .env.example .env
```

Then update `.env` with your Anthropic API key:

```text
ANTHROPIC_API_KEY=your_api_key_here
PORT=8000
```

## Run the app

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Endpoints

- `GET /`: service landing
- `GET /health`: health status check
- `POST /review`: review code
- `POST /review/batch`: review a list of code files
- `GET /docs`: Swagger UI documentation

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/review" \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b):\n    return a + b", "language": "python"}'
```

## API docs

Open `http://127.0.0.1:8000/docs` in your browser after the server starts to use the interactive Swagger UI.

## Notes

- Start the app from the repository root
- Use the local `.venv` Python to avoid dependency conflicts
- Favicon requests are handled with `204 No Content` to avoid 404 noise
