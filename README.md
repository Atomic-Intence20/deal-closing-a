# Multi-AI Agent System (Gemini) — Ready to Deploy

## What this package contains
- `orchestrator.py` — FastAPI app exposing `/run` for orchestrating agents
- `agents.py` — research, pitch, and email agents using Google Gemini (via google-genai SDK) when available; otherwise falls back to simple rule-based outputs
- `requirements.txt` — Python dependencies
- `Procfile` — run command for hosting platforms
- `.env.example` — example environment variables

## Quick deploy instructions (Render)
1. Create a GitHub repo and push these files (root of repo).
2. In Render: New → Web Service → Connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn orchestrator:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render (Settings → Environment):
   - `GEMINI_API_KEY` — your Google AI Studio (Gemini) API key (optional but recommended)
   - `API_KEY` — a secret used for simple endpoint auth (optional)
   - `GEMINI_MODEL` — optional model (default: gemini-1.5-flash)
6. Deploy and test:
   - Health check: `GET /health`
   - Run agent: `POST /run` with JSON body:{"url":"https://example.com"} or {"lead_text":"..."}

## Notes
- If `GEMINI_API_KEY` is not provided or google-genai isn't available, agents fall back to simple rule-based text.
- Gemini model availability may vary by Google project; check Google AI Studio / Vertex AI docs if you see model errors.
