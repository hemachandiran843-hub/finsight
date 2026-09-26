"""Optional LLM integration via an OpenAI-compatible API configured in .env.

If no API key is configured (LLM_API_KEY empty) the platform runs in Demo Mode
and every caller must fall back to the rule-based / curated path.
"""
import json

import httpx

from config import AI_ENABLED, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE

SYSTEM_RULES = """You are FinSight X, a financial analysis assistant for bank credit and risk teams.
STRICT SAFETY RULES:
- Never predict stock prices. Never give buy/sell recommendations.
- Never approve or reject loans. Never allege or imply fraud.
- Use ONLY the provided report excerpts. If the answer is not in them, say so.
- Cite the page number of each excerpt you use, like [p.4].
- Distinguish clearly: Reported Fact vs AI Analysis vs Potential Significance.
Answer in concise, professional banking language."""


async def chat(messages: list[dict], max_tokens: int = 900) -> str | None:
    """Return model text, or None when unavailable/failed (caller falls back)."""
    if not AI_ENABLED:
        return None
    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_RULES}] + messages,
        "temperature": LLM_TEMPERATURE,
        "max_tokens": max_tokens,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None


async def summarize_report(pages: list[dict], metrics: dict) -> dict | None:
    """Ask the LLM for an executive summary JSON. Returns None on any failure."""
    context = "\n\n".join(f"[page {p['page']}]\n{p['text'][:2600]}" for p in pages[:12])
    metrics_s = json.dumps(metrics, indent=1)[:2200]
    prompt = (
        "From the report excerpts below, produce STRICT JSON with keys: "
        "headline (string), paragraphs (array of 3-5 strings), key_changes (array of strings), "
        "guidance (array of strings), risks_events (array of strings). "
        "Ground every claim in the excerpts.\n\n"
        f"EXTRACTED METRICS:\n{metrics_s}\n\nREPORT EXCERPTS:\n{context}"
    )
    text = await chat([{"role": "user", "content": prompt}], max_tokens=1200)
    if not text:
        return None
    try:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            return None
        data = json.loads(text[start:end + 1])
        if not isinstance(data.get("paragraphs"), list):
            return None
        return data
    except Exception:
        return None
