import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Lead, LeadStatus
from ..schemas import LeadCreate, LeadResponse, LeadUpdate
from ..auth import get_current_user
from ..utils.pdf_gen import generate_proposal_pdf
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY", "")
YANDEX_GPT_FOLDER_ID = os.getenv("YANDEX_GPT_FOLDER_ID", "")
YANDEX_GPT_MODEL = "yandexgpt-lite"
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


async def generate_lead_summary(chat_history: str) -> str:
    if not YANDEX_GPT_API_KEY or not YANDEX_GPT_FOLDER_ID or not chat_history.strip():
        return ""
        
    prompt = (
        "Ты — технический аналитик студии веб-разработки Khudyakov Inc. "
        "Твоя задача — проанализировать диалог клиента и подготовить ПОДРОБНУЮ "
        "техническую выжимку для специалистов. Она должна включать:\n"
        "1. Суть проекта: Что именно хочет клиент (сайт, бот, дизайн и т.д.).\n"
        "2. Требования и функционал: Какие конкретные функции обсуждались.\n"
        "3. Технологии и дизайн: Упоминал ли клиент предпочтения по стеку или стилю.\n"
        "4. Бизнес-цели: Какую проблему клиента решает этот продукт.\n"
        "Пиши структурированно, по пунктам, без лишних приветствий, но сохраняя все важные детали."
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
async def create_lead(lead: LeadCreate, db: AsyncSession = Depends(get_db)):
    # Генерируем ИИ-саммари на основе диалога
    summary = await generate_lead_summary(lead.chat_history)

    # Сохраняем в базу данных
    db_lead = Lead(
        name=lead.name,
        contact=lead.contact,
        chat_history=lead.chat_history,
        ai_summary=summary,
        status=LeadStatus.NEW
    )
    db.add(db_lead)
    await db.commit()
    await db.refresh(db_lead)

    # Forward to our new local Telegram bot microservice
    url = "http://telegram_bot:8001/send_lead"
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


@router.get("/", response_model=list[LeadResponse])
async def get_leads(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    result = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
    return result.scalars().all()


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
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
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
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
