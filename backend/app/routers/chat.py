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
    "Ты — IT-эксперт и менеджер проектов веб-студии Khudyakov Inc. "
    "Мы занимаемся только веб-разработкой: премиальные веб-приложения и сайты. "
    "ЦЕНЫ: Лендинги от 60к, Магазины от 150к, Визитки от 40к. "
    "СРОКИ: Лендинг и визитка — от 2-х недель. Сложные проекты (магазины, сервисы) оцениваются индивидуально под задачу.\n"
    "Мобильные приложения НЕ делаем.\n\n"
    "ПРАВИЛА И ОГРАНИЧЕНИЯ:\n"
    "- Отвечай КРАТКО! Максимум 3-4 небольших предложения или короткий список.\n"
    "- НЕ используй символы * и #. Вообще никогда.\n"
    "- НЕ пиши код и не обсуждай конкурентов.\n"
    "- ЕСЛИ СПРАШИВАЮТ НЕ ПРО IT (рецепты, погода, стихи) — вежливо возвращай разговор на веб-разработку: 'Я специализируюсь на создании сайтов. Чем могу помочь вашему бизнесу?'.\n\n"
    "ЗАДАЧА В ДИАЛОГЕ:\n"
    "Веди диалог. Если абстрактная идея — задай 1 уточняющий вопрос (дизайн, функционал, ниша).\n"
    "Если дают ТЗ — назови 1-2 технологии (например, Vue+FastAPI) и кратко объясни почему. Обязательно укажи, что ТОЧНЫЙ СТЕК утверждается при заказе.\n"
    "Если говорят 'Почему так дорого?' — объясни, что мы пишем код с нуля без шаблонов, делаем SEO-оптимизацию и даем юридическую гарантию по договору.\n"
    "В конце своего сообщения НЕ предлагай сразу созвон. Спрашивай: 'У вас остались еще какие-то вопросы?'. "
    "Только когда клиент готов, призывай его нажать кнопку 'Заявка' в шапке чата для передачи контактов."
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
            "maxTokens": 500,
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
