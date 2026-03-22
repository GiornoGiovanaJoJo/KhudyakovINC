import os
import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, cast, String
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import Lead, LeadStatus, LeadPriority, LeadNote
from ..schemas import LeadCreate, LeadResponse, LeadUpdate, LeadNoteCreate, LeadNoteResponse
from ..auth import get_current_admin, get_current_user_optional
from typing import List, Optional
from fastapi import Request
from ..utils.pdf_gen import generate_proposal_pdf
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

INTERNAL_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "super-secret-service-key")

router = APIRouter()

YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY", "")
YANDEX_GPT_FOLDER_ID = os.getenv("YANDEX_GPT_FOLDER_ID", "")
YANDEX_GPT_MODEL = "yandexgpt-lite"
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


async def generate_lead_summary(chat_history: str) -> str:
    if not YANDEX_GPT_API_KEY or not YANDEX_GPT_FOLDER_ID or not chat_history.strip():
        return ""
        
    prompt = (
        "Ты — технический аналитик и квалификатор лидов студии Khudyakov Inc. "
        "Твоя задача — проанализировать диалог клиента и подготовить ПОДРОБНУЮ "
        "структурированную выжимку для команды. Она должна включать:\n\n"
        "1. ТЕМПЕРАТУРА ЛИДА:\n"
        "   - Горячий — клиент чётко знает что хочет, готов к сделке.\n"
        "   - Тёплый — интересуется, но нужна доработка (уточнения, обсуждение бюджета).\n"
        "   - Холодный — только присматривается, конкретики мало.\n\n"
        "2. СУТЬ ПРОЕКТА: Что именно хочет клиент (сайт, бот, дизайн, приложение и т.д.).\n\n"
        "3. ТРЕБОВАНИЯ И ФУНКЦИОНАЛ: Какие конкретные функции и особенности обсуждались.\n\n"
        "4. БЮДЖЕТ И СРОКИ: Если клиент упоминал бюджет или дедлайн — выдели отдельно. Если нет — укажи 'не обсуждалось'.\n\n"
        "5. ТЕХНОЛОГИИ И ДИЗАЙН: Упоминал ли клиент предпочтения по стеку, платформе или стилю.\n\n"
        "6. БИЗНЕС-ЦЕЛИ: Какую проблему клиента решает этот продукт.\n\n"
        "7. РЕКОМЕНДАЦИЯ — КОМУ ПЕРЕДАТЬ:\n"
        "   - Дизайнеру (если проект про визуал, UI/UX, логотипы)\n"
        "   - Frontend (если нужна верстка, анимации, SPA)\n"
        "   - Backend (если нужны боты, интеграции, API, базы данных)\n"
        "   - Всей команде (проект под ключ)\n\n"
        "Пиши структурированно, по пунктам, без лишних приветствий. Сохраняй все важные детали из диалога."
    )
    
    messages = [
        {"role": "system", "text": prompt},
        {"role": "user", "text": f"ДИАЛОГ:\n{chat_history[-5000:]}"} # Увеличиваем контекст
    ]
    
    payload = {
        "modelUri": f"gpt://{YANDEX_GPT_FOLDER_ID}/{YANDEX_GPT_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 600,
        },
        "messages": messages,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_GPT_API_KEY}",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(YANDEX_GPT_URL, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            summary = data["result"]["alternatives"][0]["message"]["text"]
            return summary.replace("*", "").replace("#", "").strip()
    except Exception as e:
        logger.error(f"YandexGPT Summary error: {e}")
        return ""


@router.post("/")
async def create_lead(
    lead: LeadCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    # Determine user_id if logged in
    user_id = None
    if current_user:
        try:
            user_id = int(current_user["id"])
        except (ValueError, TypeError, KeyError):
            pass

    # Генерируем ИИ-саммари на основе диалога
    summary = await generate_lead_summary(lead.chat_history)

    # Сохраняем в базу данных
    db_lead = Lead(
        name=lead.name,
        contact=lead.contact,
        chat_history=lead.chat_history,
        ai_summary=summary,
        status=LeadStatus.NEW,
        user_id=user_id
    )
    db.add(db_lead)
    await db.commit()
    await db.refresh(db_lead)

    # Forward to our local Telegram bot microservice (localhost for host network mode)
    url = "http://localhost:8001/send_lead"
    payload = {
        "id": db_lead.id,
        "name": lead.name,
        "contact": lead.contact,
        "chat_history": lead.chat_history,
        "ai_summary": summary,
        "is_supplement": lead.is_supplement
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Bot service error: {response.status_code} {response.text}")
                return {"status": "warning", "message": "Lead saved but bot notification failed.", "id": db_lead.id}
            return {"status": "success", "message": "Lead safely stored and forwarded.", "id": db_lead.id}
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        return {"status": "warning", "message": "Lead saved but notification failed.", "id": db_lead.id}


# ── Stats ──────────────────────────────────────────────

@router.get("/stats")
async def get_lead_stats(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    """Aggregated statistics for the dashboard (SQL-level aggregation)."""
    import datetime
    from datetime import timezone
    now = datetime.datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - datetime.timedelta(days=7)

    # Total count
    total_result = await db.execute(select(func.count(Lead.id)))
    total = total_result.scalar() or 0

    # Count by status (SQL GROUP BY)
    status_result = await db.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    )
    by_status = {}
    for row in status_result:
        s = row[0].value if hasattr(row[0], 'value') else str(row[0])
        by_status[s] = row[1]

    # Count by priority (SQL GROUP BY)
    priority_result = await db.execute(
        select(Lead.priority, func.count(Lead.id)).group_by(Lead.priority)
    )
    by_priority = {}
    for row in priority_result:
        p = row[0].value if row[0] and hasattr(row[0], 'value') else (str(row[0]) if row[0] else "warm")
        by_priority[p] = row[1]

    # Today count
    today_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.created_at >= today_start)
    )
    today_count = today_result.scalar() or 0

    # Week count
    week_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.created_at >= week_start)
    )
    week_count = week_result.scalar() or 0

    # Conversion rate
    completed = by_status.get("completed", 0)
    conversion = round((completed / total * 100), 1) if total > 0 else 0

    # Recent leads (last 7 days) — only this small subset loaded
    recent_result = await db.execute(
        select(Lead.created_at).where(Lead.created_at >= week_start)
    )
    daily = {}
    for row in recent_result:
        if row[0]:
            day = row[0].strftime("%d.%m")
            daily[day] = daily.get(day, 0) + 1

    return {
        "total": total,
        "today": today_count,
        "week": week_count,
        "conversion": conversion,
        "by_status": by_status,
        "by_priority": by_priority,
        "daily": daily,
    }


@router.get("/count/new")
async def get_new_leads_count(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    result = await db.execute(select(Lead).where(Lead.status == LeadStatus.NEW))
    return {"count": len(result.scalars().all())}


@router.get("/search")
async def search_leads(
    q: str,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    """Search leads by name, contact, or AI summary."""
    # Escape LIKE-special characters to prevent wildcard injection
    safe_q = q.replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{safe_q}%"
    query = select(Lead).where(
        Lead.name.ilike(pattern) |
        Lead.contact.ilike(pattern) |
        Lead.ai_summary.ilike(pattern)
    ).order_by(Lead.created_at.desc())
    result = await db.execute(query)
    leads = result.scalars().all()
    return [LeadResponse.model_validate(l) for l in leads]


@router.get("/", response_model=list[LeadResponse])
async def get_leads(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    result = await db.execute(
        select(Lead)
        .options(selectinload(Lead.notes))
        .order_by(Lead.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Determine if authorized (either by internal secret for the bot or admin JWT)
    authorized = False
    
    # 1. Check for internal service secret
    secret = request.headers.get("X-Internal-Secret")
    if secret == INTERNAL_SECRET:
        authorized = True
    
    # 2. If not internal, verify admin JWT properly
    if not authorized:
        from jose import jwt, JWTError
        from ..auth import JWT_SECRET, JWT_ALGORITHM
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authorized")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("type") != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    db_lead = await db.get(Lead, lead_id)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead_update.status is not None:
        db_lead.status = lead_update.status
    if lead_update.priority is not None:
        db_lead.priority = lead_update.priority
    
    await db.commit()
    await db.refresh(db_lead)
    return db_lead


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    """Delete a lead permanently."""
    db_lead = await db.get(Lead, lead_id)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    await db.delete(db_lead)
    await db.commit()
    return {"status": "ok", "message": f"Lead #{lead_id} deleted"}


# ── Notes ──────────────────────────────────────────────

@router.get("/{lead_id}/notes", response_model=list[LeadNoteResponse])
async def get_lead_notes(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    result = await db.execute(
        select(LeadNote)
        .where(LeadNote.lead_id == lead_id)
        .order_by(LeadNote.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{lead_id}/notes", response_model=LeadNoteResponse)
async def add_lead_note(
    lead_id: int,
    note: LeadNoteCreate,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    db_lead = await db.get(Lead, lead_id)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db_note = LeadNote(
        lead_id=lead_id,
        author=admin_username,
        text=note.text,
    )
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@router.delete("/{lead_id}/notes/{note_id}")
async def delete_lead_note(
    lead_id: int,
    note_id: int,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    db_note = await db.get(LeadNote, note_id)
    if not db_note or db_note.lead_id != lead_id:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await db.delete(db_note)
    await db.commit()
    return {"status": "ok"}


# ── Proposal PDF ───────────────────────────────────────

@router.get("/{lead_id}/proposal")
async def get_lead_proposal(
    lead_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    authorized = False
    secret = request.headers.get("X-Internal-Secret")
    if secret == INTERNAL_SECRET:
        authorized = True
    
    if not authorized:
        from jose import jwt, JWTError
        from ..auth import JWT_SECRET, JWT_ALGORITHM
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authorized")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("sub") is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    db_lead = await db.get(Lead, lead_id)
    if not db_lead or not db_lead.ai_summary:
        raise HTTPException(status_code=404, detail="Lead or summary not found")
    
    pdf_buffer = generate_proposal_pdf(db_lead.name, db_lead.ai_summary)
    
    filename = f"Proposal_{db_lead.name.replace(' ', '_')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/status/check")
async def check_lead_status(contact: str, db: AsyncSession = Depends(get_db)):
    """Public endpoint to check lead status by contact."""
    result = await db.execute(
        select(Lead)
        .where(Lead.contact == contact)
        .order_by(Lead.created_at.desc())
    )
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Заявка с таким контактом не найдена")
    
    return {
        "id": lead.id,
        "status": lead.status,
        "created_at": lead.created_at,
        "name": lead.name
    }
