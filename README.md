# AI CRM Automation System

A portfolio-ready CRM automation project built with **FastAPI, SQLite, OpenAI-compatible lead analysis, webhooks and n8n**.

It receives inbound leads, scores and prioritizes them, generates a Turkish reply draft, stores them in a lightweight CRM database and can forward processed lead data to an n8n webhook.

## Features

- Lead intake via web form and REST API
- AI-powered lead scoring and priority classification
- Turkish AI reply draft generation
- Offline fallback scoring when no OpenAI API key is configured
- SQLite CRM storage
- Lead status tracking
- Dashboard with total leads, average score and high-priority count
- Outbound webhook support for n8n
- Importable n8n workflow example
- Swagger/OpenAPI documentation

## Tech Stack

- Python
- FastAPI
- SQLite
- OpenAI API (optional)
- n8n
- REST API / Webhooks
- Jinja2
- HTML / CSS

## Project Structure

```text
ai-crm-automation-system/
├── app.py
├── ai_service.py
├── database.py
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── n8n/
│   └── lead-automation-workflow.json
└── test_app.py
```

## Installation

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment file:

```bash
copy .env.example .env
```

Run the application:

```bash
uvicorn app:app --reload
```

Open:

- Dashboard: `http://127.0.0.1:8000`
- Swagger API docs: `http://127.0.0.1:8000/docs`

## OpenAI Integration

The project works without an API key by using a deterministic fallback lead scoring engine.

To enable AI analysis, set:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Never commit your `.env` file or API key to GitHub.

## Example API Request

```bash
curl -X POST "http://127.0.0.1:8000/api/leads" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ayse Yilmaz",
    "email": "ayse@example.com",
    "company": "Acme",
    "message": "CRM ve WhatsApp otomasyonu icin acil fiyat teklifi almak istiyoruz.",
    "source": "website"
  }'
```

Example response:

```json
{
  "id": 1,
  "name": "Ayse Yilmaz",
  "score": 85,
  "priority": "high",
  "summary": "CRM ve WhatsApp otomasyonu icin acil fiyat teklifi almak istiyoruz.",
  "reply_draft": "Merhaba, mesajiniz icin tesekkur ederiz...",
  "status": "new"
}
```

## n8n Workflow

Import:

```text
n8n/lead-automation-workflow.json
```

The sample workflow:

1. Receives a lead through an n8n webhook.
2. Sends the payload to this FastAPI CRM API.
3. Checks whether the lead score is 75 or above.
4. Can be extended with Gmail, Slack, WhatsApp, Telegram or CRM nodes.

If n8n runs inside Docker and FastAPI runs on Windows, the example uses:

```text
http://host.docker.internal:8000/api/leads
```

## Portfolio Value

This project demonstrates practical experience with:

- AI service integration
- API and webhook design
- n8n automation
- CRM workflows
- backend development
- database operations
- lead qualification automation
- MVP development

## Security Notes

- `.env` is ignored by Git.
- Do not hard-code API keys.
- Add authentication, rate limiting and a production database before production use.

## License

MIT-friendly portfolio project. Add an MIT LICENSE file if you want to distribute it publicly.
