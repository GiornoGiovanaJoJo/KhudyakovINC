import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..schemas import ChatRequest, ChatResponse
from ..database import get_db
from ..models import TeamMember
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY", "")
YANDEX_GPT_FOLDER_ID = os.getenv("YANDEX_GPT_FOLDER_ID", "")
YANDEX_GPT_MODEL = "yandexgpt-lite"
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

BASE_SYSTEM_PROMPT = (
    "Ты — ведущий IT-эксперт и менеджер проектов студии Khudyakov Inc. "
    "Ваша студия специализируется на создании премиальных цифровых продуктов: современные веб-приложения, "
    "корпоративные сайты, уникальный дизайн (UI/UX, логотипы, брендинг), сложные интеграции и Telegram-боты.\n\n"
    "ТВОЙ СТИЛЬ ОБЩЕНИЯ:\n"
    "- Дружелюбный, профессиональный, экспертный. "
    "- Если запрос общий — отвечай лаконично. Если клиент просит 'детально' или задает конкретные вопросы — "
    "давай развернутый, структурированный ответ, раскрывающий нашу экспертизу.\n"
    "- Старайся избегать шаблонных фраз. Твоя задача — не просто выдать сухой список, а объяснить, "
    "как наши решения помогут бизнесу клиента.\n\n"
    "ОРИЕНТИРЫ ПО ЦЕНАМ И СРОКАМ (примерные):\n"
    "- Лендинги: от 60к руб., от 2 недель.\n"
    "- Малые сайты/визитки: от 40к руб., от 2 недель.\n"
    "- Интернет-магазины: от 150к руб., от месяца.\n\n"
    "ПРАВИЛА И ОГРАНИЧЕНИЯ:\n"
    "- НИКОГДА не используй символы * и # в тексте.\n"
    "- Не пиши код. Не обсуждай конкурентов.\n"
    "- Мы НЕ делаем нативные мобильные приложения (iOS/Android). Предлагай вместо них PWA (веб-приложения) или ботов.\n"
    "- Если спрашивают технологии, которых нет в нашем стеке (например, Go, Ruby), вежливо отвечай, что мы "
    "фокусируемся на нашем профильном стеке (Python/Node.js/Vue), так как в нем мы достигли максимальной экспертизы.\n\n"
    "КАК РАСПИСЫВАТЬ ДЕТАЛЬНО:\n"
    "Если просят подробностей, структурируй ответ так:\n"
    "1. Подход: Как мы анализируем бизнес-задачи клиента.\n"
    "2. Технологии: Расскажи подробнее про наш стек (выбирай из предоставленного ниже списка).\n"
    "3. Визуал и UX: Упомяни про важность дизайна и удобства использования.\n"
    "4. Надежность: Расскажи про тестирование, поддержку и масштабируемость.\n\n"
    "В конце сообщения, если диалог подходит к логическому завершению, направляй клиента на кнопку 'Заявка' "
    "для обсуждения деталей с живым специалистом."
)


@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    if not YANDEX_GPT_API_KEY or not YANDEX_GPT_FOLDER_ID:
        # Fallback: если ключи не настроены, вернуть заглушку
        return ChatResponse(
            reply="Чат-бот пока не настроен. Свяжитесь с нами напрямую для консультации!"
        )

    # Динамически получаем стек технологий команды
    from sqlalchemy import select
    result = await db.execute(select(TeamMember))
    team_members = result.scalars().all()
    all_stacks = []
    for member in team_members:
        if member.stack:
            # Разбиваем по запятым и убираем лишние пробелы
            stacks = [s.strip() for s in member.stack.split(",")]
            all_stacks.extend(stacks)
    
    # Оставляем только уникальные технологии
    unique_stacks = list(set(all_stacks))
    stack_text = ", ".join(unique_stacks) if unique_stacks else "Vue.js, Nuxt 3, Node.js, FastAPI, Python"

    dynamic_prompt = BASE_SYSTEM_PROMPT + f"\n\nНАШ СТЕК (выбирай только нужное):\n{stack_text}"
    
    if data.has_submitted_lead:
        dynamic_prompt += (
            "\n\nВАЖНО: Клиент УЖЕ оставил заявку! Если он задает новые вопросы по проекту или дает новые вводные, "
            "ответь на них и ОБЯЗАТЕЛЬНО уточни: 'У вас есть еще вопросы, или вы хотите дополнить вашу заявку новыми деталями? "
            "Если да, нажмите кнопку Дополнить сверху'."
        )

    messages = [{"role": "system", "text": dynamic_prompt}]

    for msg in data.history:
        messages.append({"role": msg.role, "text": msg.text})

    messages.append({"role": "user", "text": data.message})

    payload = {
        "modelUri": f"gpt://{YANDEX_GPT_FOLDER_ID}/{YANDEX_GPT_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,
            "maxTokens": 1000,
        },
        "messages": messages,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_GPT_API_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(YANDEX_GPT_URL, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"[YandexGPT ERROR] Status: {response.status_code}")
                print(f"[YandexGPT ERROR] Body: {response.text}")
            response.raise_for_status()
            result = response.json()
            
            # Safe extraction
            alternatives = result.get("result", {}).get("alternatives", [])
            if not alternatives:
                return ChatResponse(reply="Пожалуйста, давайте придерживаться делового общения. Я могу помочь с веб-разработкой!")
                
            first_alt = alternatives[0]
            message = first_alt.get("message", {})
            reply_text = message.get("text", "")
            
            if not reply_text:
                # В случае блокировки (content filter) YandexGPT не возвращает text
                print(f"[YandexGPT FILTERED]: {result}")
                return ChatResponse(reply="Извините, но я не могу поддержать этот разговор. Давайте вернемся к обсуждению веб-разработки и IT-проектов!")
                
            # Принудительно вырезаем звездочки и решетки, если ИИ их все-таки сгенерировал
            reply_text = reply_text.replace("*", "").replace("#", "")
            
            return ChatResponse(reply=reply_text.strip())
    except httpx.HTTPStatusError as e:
        print(f"[YandexGPT ERROR] HTTPStatusError: {e.response.status_code} - {e.response.text}")
        # Если 400 из-за фильтров Yandex:
        if e.response.status_code == 400:
             return ChatResponse(reply="Ваше сообщение заблокировано фильтром безопасности. Давайте общаться на рабочие темы!")
        raise HTTPException(status_code=502, detail=f"Ошибка YandexGPT: {e.response.status_code}")
    except Exception as e:
        print(f"[YandexGPT ERROR] Exception: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка чат-бота: {str(e)}")
