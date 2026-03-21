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
from aiogram.client.session.aiohttp import AiohttpSession
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
logger = logging.getLogger(__name__)

# JSON db
CHATS_FILE = "chats.json"

# ── Proxy Configuration ──────────────────────────────────────────
# Priority: PROXY_URL env var first, then fallback list
PROXY_URL_ENV = os.getenv("PROXY_URL", "")

# URLs to fetch fresh SOCKS5 proxy lists
PROXY_LIST_URLS = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
]


async def _fetch_fresh_proxies() -> list[str]:
    """Download fresh SOCKS5 proxy lists from public sources."""
    all_proxies = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for url in PROXY_LIST_URLS:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    lines = resp.text.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line and ":" in line:
                            all_proxies.append(f"socks5://{line}")
                    logger.info(f"[PROXY] Fetched {len(lines)} proxies from {url}")
            except Exception as e:
                logger.warning(f"[PROXY] Failed to fetch from {url}: {e}")
    
    # Deduplicate
    return list(dict.fromkeys(all_proxies))


async def _test_proxy(proxy_url: str, token: str) -> str | None:
    """Test if a proxy can reach Telegram API. Returns proxy_url if works, None otherwise."""
    test_bot = None
    try:
        session = AiohttpSession(proxy=proxy_url)
        test_bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        me = await asyncio.wait_for(test_bot.get_me(), timeout=8)
        await test_bot.session.close()
        logger.info(f"[PROXY] ✅ {proxy_url} works! Bot: @{me.username}")
        return proxy_url
    except Exception:
        try:
            if test_bot:
                await test_bot.session.close()
        except:
            pass
        return None


async def _find_working_proxy(token: str) -> str | None:
    """Fetch fresh proxies and test them in concurrent batches."""
    
    # 1. Try env var proxy first
    if PROXY_URL_ENV:
        logger.info(f"[PROXY] Testing env proxy: {PROXY_URL_ENV}")
        if await _test_proxy(PROXY_URL_ENV, token):
            return PROXY_URL_ENV
    
    # 2. Fetch fresh proxy lists
    proxies = await _fetch_fresh_proxies()
    if not proxies:
        logger.error("[PROXY] Could not fetch any proxy lists!")
        return None
    
    logger.info(f"[PROXY] Testing {len(proxies)} fresh proxies in batches of 10...")
    
    # 3. Test in batches of 10 concurrently (much faster)
    BATCH_SIZE = 10
    for i in range(0, min(len(proxies), 200), BATCH_SIZE):  # Test max 200
        batch = proxies[i:i + BATCH_SIZE]
        tasks = [_test_proxy(p, token) for p in batch]
        results = await asyncio.gather(*tasks)
        
        # Return the first working proxy from this batch
        for result in results:
            if result is not None:
                return result
        
        logger.info(f"[PROXY] Batch {i//BATCH_SIZE + 1} done, no working proxy yet...")
    
    logger.error("[PROXY] No working proxy found in any batch!")
    return None


# ── Global bot/dp (will be initialized in lifespan) ──────────────
bot: Bot | None = None
dp = Dispatcher()

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


# ── FastAPI Integration ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(fapi: FastAPI):
    global bot
    
    # Find a working proxy
    working_proxy = await _find_working_proxy(BOT_TOKEN)
    
    if working_proxy:
        session = AiohttpSession(proxy=working_proxy)
        bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        logger.info(f"[BOT] Started with proxy: {working_proxy}")
    else:
        # Try direct connection as last resort
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        logger.warning("[BOT] Starting WITHOUT proxy (direct connection)")
    
    task = asyncio.create_task(dp.start_polling(bot))
    yield
    task.cancel()
    try:
        await bot.session.close()
    except Exception:
        pass

app = FastAPI(title="Telegram Leads Webhook API", lifespan=lifespan)

class LeadData(BaseModel):
    id: int
    name: str
    contact: str
    chat_history: str = ""
    ai_summary: str = ""
    is_supplement: bool = False

@app.post("/send_lead")
async def send_lead(lead: LeadData):
    global bot
    
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
        safe_summary = html.escape(lead.ai_summary[:800])
        text += f"🤖 <b>AI РЕЗЮМЕ ПРОЕКТА:</b>\n"
        text += f"<i>{safe_summary}...</i>\n\n"

    text += f"💬 <b>Полная история чата:</b>\n"
    
    history_text = lead.chat_history[:2000] if lead.chat_history else "Нет истории"
    safe_history = html.escape(history_text)
    if len(lead.chat_history) > 2000:
        safe_history += "...\n[История обрезана]"
    text += f"<pre>{safe_history}</pre>"

    builder = InlineKeyboardBuilder()
    builder.button(text="🕒 В работу", callback_data=f"status_{lead.id}_in_progress")
    builder.button(text="✅ Завершено", callback_data=f"status_{lead.id}_completed")
    builder.adjust(2)
    
    success_count: int = 0
    INTERNAL_SECRET = "super-secret-service-key"
    
    for chat_id in chats:
        try:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=builder.as_markup())
            
            try:
                backend_pdf_url = f"http://localhost:8000/api/leads/{lead.id}/proposal"
                async with httpx.AsyncClient(timeout=20.0) as client:
                    pdf_res = await client.get(backend_pdf_url, headers={"X-Internal-Secret": INTERNAL_SECRET})
                    if pdf_res.status_code == 200:
                        from aiogram.types import BufferedInputFile
                        pdf_file = BufferedInputFile(pdf_res.content, filename=f"Proposal_{lead.name.replace(' ', '_')}.pdf")
                        await bot.send_document(
                            chat_id=chat_id, 
                            document=pdf_file, 
                            caption=f"📄 Сгенерированное КП для {safe_name}"
                        )
            except Exception as pdf_err:
                logger.error(f"Failed to fetch/send PDF for lead {lead.id}: {pdf_err}")
                
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send lead to chat {chat_id}: {e}")
            
            # If proxy died, try to find a new one and retry
            if "proxy" in str(e).lower() or "connect" in str(e).lower():
                logger.info("[PROXY] Proxy seems dead, trying to find a new one...")
                new_proxy = await _find_working_proxy(BOT_TOKEN)
                if new_proxy:
                    session = AiohttpSession(proxy=new_proxy)
                    bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
                    try:
                        await bot.send_message(chat_id=chat_id, text=text, reply_markup=builder.as_markup())
                        success_count += 1
                        logger.info(f"[PROXY] Retry with new proxy succeeded!")
                    except Exception as retry_err:
                        logger.error(f"[PROXY] Retry also failed: {retry_err}")
            
    if success_count > 0:
        return {"status": "success", "messages_sent": success_count}
    else:
        raise HTTPException(status_code=500, detail="Failed to deliver to registered chats.")

@dp.callback_query(F.data.startswith("status_"))
async def handle_status_change(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        return
    
    lead_id = parts[1]
    new_status = "_".join(parts[2:])
    
    status_map = {
        "in_progress": "🕒 В РАБОТЕ",
        "completed": "✅ ЗАВЕРШЕНО"
    }
    
    INTERNAL_SECRET = "super-secret-service-key"
    backend_url = f"http://localhost:8000/api/leads/{lead_id}"
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Internal-Secret": INTERNAL_SECRET}
            response = await client.patch(backend_url, json={"status": new_status}, headers=headers)
            if response.status_code == 200:
                await callback.answer(f"Статус изменен на: {status_map.get(new_status)}")
                
                new_text = callback.message.html_text
                if "🟡 <b>СТАТУС:" in new_text:
                    lines = new_text.split("\n")
                    lines[0] = f"🟡 <b>СТАТУС: {status_map.get(new_status)}</b>"
                    new_text = "\n".join(lines)
                else:
                    new_text = f"🟡 <b>СТАТУС: {status_map.get(new_status)}</b>\n\n" + new_text
                
                await callback.message.edit_text(text=new_text, reply_markup=callback.message.reply_markup)
            else:
                await callback.answer("Ошибка при обновлении в базе данных", show_alert=True)
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        await callback.answer("Ошибка связи с бэкендом", show_alert=True)

if __name__ == "__main__":
    uvicorn.run("bot:app", host="0.0.0.0", port=8001, reload=False)
