import asyncio
import json
import logging
import os
import html
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in .env")

# Logging
logging.basicConfig(level=logging.INFO)

# JSON db
CHATS_FILE = "chats.json"

def load_chats():
    if not os.path.exists(CHATS_FILE):
        return set()
    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception:
        return set()

def save_chat(chat_id: int):
    chats = load_chats()
    if chat_id not in chats:
        chats.add(chat_id)
        with open(CHATS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(chats), f)
        return True
    return False

# Setup Bot and Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    is_new = save_chat(chat_id)
    if is_new:
        await message.answer("✅ Бот успешно подключен! Теперь заявки с сайта будут приходить в этот чат.\nИспользуйте команду /help для справки.")
    else:
        await message.answer("Этот чат уже получает заявки с сайта.\nИспользуйте команду /help для справки.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "🤖 <b>СПРАВКА:</b>\n\n"
        "Я внутренний бот студии Khudyakov Inc. Моя задача — мгновенно доставлять заявки с сайта.\n\n"
        "<b>Команды:</b>\n"
        "/start — Подключить этот чат к получению заявок\n"
        "/help — Показать эту справку\n\n"
        "Чтобы бот отправлял заявки в группу, просто добавьте его туда и напишите /start."
    )
    await message.answer(help_text)

# FastAPI Integration
app = FastAPI(title="Telegram Leads Webhook API")

class LeadData(BaseModel):
    id: int
    name: str
    contact: str
    chat_history: str = ""
    ai_summary: str = ""
    is_supplement: bool = False

@app.post("/send_lead")
async def send_lead(lead: LeadData):
    chats = load_chats()
    if not chats:
        raise HTTPException(status_code=400, detail="No active Telegram chats registered.")

    safe_name = html.escape(lead.name)
    safe_contact = html.escape(lead.contact)
    
    if lead.is_supplement:
        text = f"➕ <b>ДОПОЛНЕНИЕ К ЗАЯВКЕ!</b>\n\n"
    else:
        text = f"🔥 <b>Новая заявка с сайта!</b>\n\n"
        
    text += f"👤 <b>Имя:</b> {safe_name}\n"
    text += f"📞 <b>Контакт:</b> {safe_contact}\n\n"
    
    if lead.ai_summary:
        safe_summary = html.escape(lead.ai_summary[:1000])
        text += f"🤖 <b>AI РЕЗЮМЕ ПРОЕКТА:</b>\n"
        text += f"<i>{safe_summary}</i>\n\n"

    text += f"💬 <b>Полная история чата:</b>\n"
    
    # Режем историю и экранируем HTML
    history_text = lead.chat_history[:3000] if lead.chat_history else "Нет истории"
    safe_history = html.escape(history_text)
    text += f"<pre>{safe_history}</pre>"
    
    # Кнопки управления статусом
    builder = InlineKeyboardBuilder()
    builder.button(text="🕒 В работу", callback_data=f"status_{lead.id}_in_progress")
    builder.button(text="✅ Завершено", callback_data=f"status_{lead.id}_completed")
    builder.adjust(2)
    
    success_count: int = 0
    for chat_id in chats:
        try:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=builder.as_markup())
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to send lead to chat {chat_id}: {e}")
            
    if success_count > 0:
        return {"status": "success", "messages_sent": success_count}
    else:
        raise HTTPException(status_code=500, detail="Emails failed to deliver to registered chats.")

# Callback handler for statuses
@dp.callback_query(F.data.startswith("status_"))
async def handle_status_change(callback: types.CallbackQuery):
    _, lead_id, new_status = callback.data.split("_")
    
    # Map visual status
    status_map = {
        "in_progress": "🕒 В РАБОТЕ",
        "completed": "✅ ЗАВЕРШЕНО"
    }
    
    # Update backend
    backend_url = f"http://backend:8000/api/leads/{lead_id}"
    try:
        async with httpx.AsyncClient() as client:
            # Match INTERNAL_SECRET from backend/app/routers/leads.py
            headers = {"X-Internal-Secret": "super-secret-service-key"}
            response = await client.patch(backend_url, json={"status": new_status}, headers=headers)
            if response.status_code == 200:
                await callback.answer(f"Статус изменен на: {status_map.get(new_status)}")
                
                # Update message text to show new status
                new_text = callback.message.html_text
                if "🟡 <b>СТАТУС:" in new_text:
                    # Replace existing status
                    lines = new_text.split("\n")
                    lines[0] = f"🟡 <b>СТАТУС: {status_map.get(new_status)}</b>"
                    new_text = "\n".join(lines)
                else:
                    # Add new status at the top
                    new_text = f"🟡 <b>СТАТУС: {status_map.get(new_status)}</b>\n\n" + new_text
                
                await callback.message.edit_text(text=new_text, reply_markup=callback.message.reply_markup)
            else:
                await callback.answer("Ошибка при обновлении в базе данных", show_alert=True)
    except Exception as e:
        logging.error(f"Error updating status: {e}")
        await callback.answer("Ошибка связи с бэкендом", show_alert=True)

async def start_bot():
    # start polling
    await dp.start_polling(bot)

@app.on_event("startup")
async def on_startup():
    # Start bot polling in background
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    uvicorn.run("bot:app", host="0.0.0.0", port=8001, reload=False)
