import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from agents import research_agent, pitch_agent, email_agent
import uvicorn

API_KEY = os.environ.get("API_KEY")  # optional simple auth for endpoints
PORT = int(os.environ.get("PORT", 8000))

app = FastAPI(title="Multi-AI Agent Orchestrator (Gemini)")

class RunPayload(BaseModel):
    task: str = None
    url: str = None
    lead_text: str = None

def check_auth(request: Request):
    if API_KEY:
        header = request.headers.get("x-api-key")
        if header != API_KEY:
            raise HTTPException(status_code=401, detail="Missing or invalid x-api-key header")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/run")
async def run(payload: RunPayload, request: Request):
    check_auth(request)

    # Decide which agent to use from payload.task or payload content
    text = None
    if payload.lead_text:
        text = payload.lead_text
    elif payload.url:
        # fetch & summarize via research agent
        text = research_agent.scrape_and_summarize(payload.url)
    elif payload.task:
        text = payload.task

    if not text:
        raise HTTPException(status_code=400, detail="Provide at least one of: task, url, or lead_text")

    # Simple routing: keywords determine agent
    low = (payload.task or "").lower() + " " + (text or "").lower()
    if "pitch" in low or "proposal" in low:
        pitch = pitch_agent.create_pitch(text)
        return {"agent": "pitch_agent", "output": pitch}
    elif "email" in low or "follow" in low:
        mail = email_agent.create_email(text)
        return {"agent": "email_agent", "output": mail}
    else:
        # Default: research -> pitch suggestion
        analysis = research_agent.analyze_needs(text)
        pitch = pitch_agent.create_pitch(analysis.get("top_hints", []), text)
        return {"agent": "research+pitch", "analysis": analysis, "pitch": pitch}

if __name__ == '__main__':
    uvicorn.run("orchestrator:app", host="0.0.0.0", port=PORT, log_level="info")
