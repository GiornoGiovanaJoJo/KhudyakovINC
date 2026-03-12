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
        "Ты — аналитик студии веб-разработки Khudyakov Inc. "
        "Прочитай диалог клиента с ИИ-менеджером и сделай ОЧЕНЬ КРАТКУЮ "
        "выжимку (2-3 предложения) того, что нужно клиенту. "
        "Что за проект, какой функционал, есть ли дизайн. Только факты, без воды."
    )
    
    messages = [
        {"role": "system", "text": prompt},
        {"role": "user", "text": f"ДИАЛОГ:\n{chat_history[-3000:]}"} # Ограничиваем историю
    ]
    
    payload = {
        "modelUri": f"gpt://{YANDEX_GPT_FOLDER_ID}/{YANDEX_GPT_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 300,
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

    # Forward to our new local Telegram bot microservice instead of direct API
    url = "http://127.0.0.1:8001/send_lead"
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
                print(f"[ERROR] Bot microservice returned {response.status_code}: {response.text}")
                # Don't strictly throw if bot fails, just warn
                return {"status": "warning", "message": "Lead received but bot failed to broadcast."}
            return {"status": "success", "message": "Lead safely forwarded to Telegram bot."}
    except httpx.RequestError as e:
        print(f"[ERROR] Failed to contact Telegram bot microservice: {str(e)}")
        # Lead is saved in DB in the future maybe, but right now it fails.
        raise HTTPException(status_code=500, detail="Ошибка связи с сервисом уведомлений.")
