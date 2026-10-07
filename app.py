import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ai_service import analyze_lead
from database import get_connection, init_db

load_dotenv()
BASE_DIR = Path(__file__).parent

app = FastAPI(title="AI CRM Automation System", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    message: str
    source: str = "api"


@app.on_event("startup")
def startup():
    init_db()


async def notify_n8n(payload: dict):
    url = os.getenv("N8N_WEBHOOK_URL")
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            await client.post(url, json=payload)
    except Exception:
        pass


async def create_lead_record(data: LeadCreate):
    analysis = await analyze_lead(data.message, data.company)
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO leads(name,email,phone,company,message,source,score,priority,summary,reply_draft)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                data.name, data.email, data.phone, data.company, data.message, data.source,
                analysis["score"], analysis["priority"], analysis["summary"], analysis["reply_draft"]
            ),
        )
        lead_id = cur.lastrowid
        conn.commit()
    result = {"id": lead_id, **data.model_dump(), **analysis, "status": "new"}
    await notify_n8n(result)
    return result


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    with get_connection() as conn:
        leads = conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 50").fetchall()
        stats = conn.execute(
            "SELECT COUNT(*) as total, ROUND(AVG(score),1) as avg_score, SUM(CASE WHEN priority='high' THEN 1 ELSE 0 END) as high_count FROM leads"
        ).fetchone()
    return templates.TemplateResponse("index.html", {"request": request, "leads": leads, "stats": stats})


@app.post("/web-lead")
async def web_lead(
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    company: str = Form(""),
    message: str = Form(...),
):
    await create_lead_record(LeadCreate(name=name, email=email or None, phone=phone or None, company=company or None, message=message, source="web"))
    return RedirectResponse(url="/", status_code=303)


@app.post("/api/leads")
async def create_lead(data: LeadCreate):
    return await create_lead_record(data)


@app.get("/api/leads")
def list_leads():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


@app.patch("/api/leads/{lead_id}/status")
def update_status(lead_id: int, status: str):
    allowed = {"new", "contacted", "qualified", "won", "lost"}
    if status not in allowed:
        return {"ok": False, "error": "invalid status"}
    with get_connection() as conn:
        cur = conn.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))
        conn.commit()
    return {"ok": cur.rowcount > 0, "id": lead_id, "status": status}


@app.get("/health")
def health():
    return {"status": "ok"}
