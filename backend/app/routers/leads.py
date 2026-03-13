import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY", "")
YANDEX_GPT_FOLDER_ID = os.getenv("YANDEX_GPT_FOLDER_ID", "")
YANDEX_GPT_MODEL = "yandexgpt-lite"
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

class LeadCreate(BaseModel):
    name: str
    contact: str
    chat_history: str = ""
    is_supplement: bool = False

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
async def create_lead(lead: LeadCreate):
    # Генерируем ИИ-саммари на основе диалога
    summary = await generate_lead_summary(lead.chat_history)

    # Forward to our new local Telegram bot microservice
    url = "http://telegram_bot:8001/send_lead"
    payload = {
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
                raise HTTPException(status_code=500, detail="Не удалось отправить уведомление в Telegram.")
            return {"status": "success", "message": "Lead safely forwarded to Telegram bot."}
    except httpx.RequestError as e:
        print(f"[ERROR] Failed to contact Telegram bot microservice: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка связи с сервисом уведомлений: {str(e)}"
        )
    except Exception as e:
        print(f"[CRITICAL ERROR] Unexpected failure in create_lead: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Произошла непредвиденная ошибка на сервере: {str(e)}"
        )
