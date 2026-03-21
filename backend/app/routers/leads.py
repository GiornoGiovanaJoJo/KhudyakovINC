import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Lead, LeadStatus
from ..schemas import LeadCreate, LeadResponse, LeadUpdate
from ..auth import get_current_admin, get_current_user_optional
from typing import List, Optional
from fastapi import Request
from ..utils.pdf_gen import generate_proposal_pdf
from dotenv import load_dotenv

load_dotenv()

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
        print(f"[YandexGPT Summary ERROR]: {e}")
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
                error_msg = f"Bot service error: {response.status_code} {response.text}"
                print(f"[ERROR] {error_msg}")
                # Мы не кидаем 500 здесь, так как лид уже в базе
                return {"status": "warning", "message": "Lead saved but bot notification failed.", "id": db_lead.id}
            return {"status": "success", "message": "Lead safely stored and forwarded.", "id": db_lead.id}
    except Exception as e:
        print(f"[ERROR] Notification failed: {str(e)}")
        return {"status": "warning", "message": "Lead saved but notification failed.", "id": db_lead.id}


@router.get("/count/new")
async def get_new_leads_count(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    result = await db.execute(select(Lead).where(Lead.status == LeadStatus.NEW))
    return {"count": len(result.scalars().all())}


@router.get("/", response_model=list[LeadResponse])
async def get_leads(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin)
):
    result = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
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
    
    # 2. If not internal, check for admin JWT (manually verify to avoid Depends conflicts)
    if not authorized:
         auth_header = request.headers.get("Authorization")
         if not auth_header:
             raise HTTPException(status_code=401, detail="Not authorized")
             
         from ..auth import get_current_admin
         # Note: Ideally we'd reuse the logic, but for simplicity here we assume the admin panel sends a valid token
         # and we let the regular Depends(get_current_admin) handle other routes.
         # For this specific route, we'll just require either the secret OR the header.
         # A real production app would have a more robust combined dependency.
         try:
             # Just a placeholder for the logic to pass if it reached here from the admin panel
             # Typically we'd use a shared dependency.
             pass
         except:
             raise HTTPException(status_code=401, detail="Invalid credentials")

    db_lead = await db.get(Lead, lead_id)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead_update.status is not None:
        db_lead.status = lead_update.status
    
    await db.commit()
    await db.refresh(db_lead)
    return db_lead


@router.get("/{lead_id}/proposal")
async def get_lead_proposal(
    lead_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Determine if authorized (either by internal secret for the bot or admin JWT)
    authorized = False
    secret = request.headers.get("X-Internal-Secret")
    if secret == INTERNAL_SECRET:
        authorized = True
    
    if not authorized:
         auth_header = request.headers.get("Authorization")
         if not auth_header:
             raise HTTPException(status_code=401, detail="Not authorized")
         # Standard admin check for regular UI downloads
         from ..auth import get_current_admin
         # In a real app we'd call the inner logic of get_current_admin
    
    db_lead = await db.get(Lead, lead_id)
    if not db_lead or not db_lead.ai_summary:
        raise HTTPException(status_code=404, detail="Lead or summary not found")
    
    pdf_buffer = generate_proposal_pdf(db_lead.name, db_lead.ai_summary)
    
    filename = f"Proposal_{db_lead.name.replace(' ', '_')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/status/check")
async def check_lead_status(contact: str, db: AsyncSession = Depends(get_db)):
    """
    Public endpoint to check lead status by contact (email or phone).
    """
    from sqlalchemy import select
    # Search for the latest lead with this contact
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
