import json
import os
import re
import httpx


def fallback_analysis(message: str, company: str | None = None) -> dict:
    text = (message or "").lower()
    score = 35

    high_intent = ["teklif", "fiyat", "satın", "demo", "toplantı", "entegrasyon", "acil", "hemen"]
    medium_intent = ["bilgi", "detay", "özellik", "otomasyon", "crm", "yapay zeka", "ai"]

    score += sum(10 for kw in high_intent if kw in text)
    score += sum(5 for kw in medium_intent if kw in text)
    if company:
        score += 10
    score = min(score, 100)

    priority = "high" if score >= 75 else "medium" if score >= 50 else "low"
    summary = (message[:180] + "...") if len(message) > 180 else message
    reply = (
        "Merhaba, mesajınız için teşekkür ederiz. Talebinizi aldık ve ilgili ekip arkadaşımız kısa süre içinde "
        "sizinle iletişime geçecektir. Dilerseniz ihtiyacınızı biraz daha detaylandırabilirsiniz."
    )
    return {"score": score, "priority": priority, "summary": summary or "Mesaj içeriği yok.", "reply_draft": reply}


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


async def analyze_lead(message: str, company: str | None = None) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    if not api_key:
        return fallback_analysis(message, company)

    prompt = f"""
You are a CRM lead qualification assistant.
Return ONLY valid JSON with these keys: score (0-100 integer), priority (low|medium|high), summary, reply_draft.
Analyze this inbound lead.
Company: {company or 'unknown'}
Message: {message}
The reply_draft must be in Turkish, polite, concise and sales-oriented without making promises.
""".strip()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You classify CRM leads and return strict JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = _extract_json(content)
        if not parsed:
            return fallback_analysis(message, company)
        parsed["score"] = max(0, min(int(parsed.get("score", 50)), 100))
        parsed["priority"] = parsed.get("priority", "medium")
        return parsed
