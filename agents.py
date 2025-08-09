import os, textwrap
import requests
from bs4 import BeautifulSoup

# Try to import Google Gen AI SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
# Client will be created lazily
_genai_client = None
def get_genai_client():
    global _genai_client
    if _genai_client is None and GENAI_AVAILABLE:
        # The SDK reads GEMINI_API_KEY from env by default
        _genai_client = genai.Client()
    return _genai_client

# ---------------------- Research Agent ----------------------
class research_agent:
    @staticmethod
    def scrape_website(url, timeout=10):
        headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.text

    @staticmethod
    def scrape_and_summarize(url):
        try:
            html = research_agent.scrape_website(url)
            soup = BeautifulSoup(html, 'html.parser')
            text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p","h1","h2","h3"]))[:8000]
        except Exception as e:
            text = f"(scrape failed: {e})"

        # If GenAI is available, ask Gemini to summarize
        if GENAI_AVAILABLE:
            client = get_genai_client()
            prompt = f"Summarize the following website content in 3 short bullets:\n\n{text[:4000]}"
            try:
                resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
                return getattr(resp, 'text', str(resp))[:4000]
            except Exception as e:
                # fall back
                return text[:2000] + "\n\n(summary failed: " + str(e) + ")"
        else:
            # naive summary: first 800 chars + small cleaning
            return ' '.join(text.split())[:1200]

    @staticmethod
    def analyze_needs(text):
        low = (text or "").lower()
        score = 0
        hints = []
        keywords = {                'slow': 'Performance/Speed issues',                'cost': 'Cost/price concerns',                'error': 'Stability / errors',                'support': 'Support / onboarding needs',                'scale': 'Scaling / architecture concerns',            }
        for k,v in keywords.items():
            if k in low:
                hints.append(v); score += 1
        if GENAI_AVAILABLE and len(hints) < 2:
            # ask Gemini for extra insights
            client = get_genai_client()
            try:
                prompt = f"Given this text, list the top 3 business pain points as short phrases:\n\n{text[:2000]}"
                resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
                extra = getattr(resp,'text', str(resp))
                # take first lines as hints
                for line in extra.split('\n'):
                    line = line.strip()
                    if line: hints.append(line)
            except Exception:
                pass
        if not hints:
            hints = ['Improve conversions / reduce churn (general)']
        return {'top_hints': hints, 'confidence': min(0.9, 0.2 + 0.2*score)}

# ---------------------- Pitch Agent ----------------------
class pitch_agent:
    @staticmethod
    def create_pitch(analysis_or_hints, research_text):
        # analysis_or_hints may be dict or list
        if isinstance(analysis_or_hints, dict):
            hints = analysis_or_hints.get('top_hints', [])
        else:
            hints = list(analysis_or_hints) if analysis_or_hints else []
        hint = hints[0] if hints else 'improve conversions'
        snippet = (research_text or '')[:800].replace('\n',' ')
        template = textwrap.dedent(f"""                Hi there,

            We reviewed your site and noticed: {hint}.
            Quick summary: {snippet}...

            Our proposal: a tailored quick win that addresses {hint.lower()} and improves outcomes within 30 days.
            Would you be open to a 15-minute call to discuss a custom plan?

            Best,
            Deal-Closing Team
        """).strip()

        # If GenAI available, ask Gemini to polish the pitch
        if GENAI_AVAILABLE:
            client = get_genai_client()
            prompt = ("Rewrite the following sales pitch to be succinct and persuasive in 3 short paragraphs:\n\n" + template)
            try:
                resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
                return getattr(resp, 'text', str(resp))
            except Exception as e:
                return template + "\n\n(polite rewrite failed: " + str(e) + ")"
        else:
            return template

# ---------------------- Email Agent ----------------------
class email_agent:
    @staticmethod
    def create_email(context_text):
        snippet = (context_text or '')[:1000].replace('\n',' ')
        simple = f"Hi,\n\nFollowing up on our conversation. Quick note: {snippet[:200]}...\n\nRegards"
        if GENAI_AVAILABLE:
            client = get_genai_client()
            prompt = "Write a short professional follow-up email based on:\n\n" + snippet
            try:
                resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
                return getattr(resp, 'text', str(resp))
            except Exception as e:
                return simple + "\n\n(fallback: " + str(e) + ")"
        else:
            return simple
