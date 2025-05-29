import logging
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from dictionaries import process_api_response_to_string

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


load_dotenv()
TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
MW_THESAURUS_API_KEY: str | None = os.getenv("MW_THESAURUS_KEY")
MW_DICTIONARY_API_KEY: str | None = os.getenv("MW_DICTIONARY_KEY")

WEBHOOK_URL = f"https://bot.theteacat.cc/webhook/{TELEGRAM_BOT_TOKEN}"
WEBHOOK_PATH = f"/webhook/{TELEGRAM_BOT_TOKEN}"
PORT = int(os.environ.get("PORT", 8000))


app = FastAPI(title="Telegram bot API", version="0.0.1")


def get_mv_thesaurus_output(word: str) -> str | None:
    response = requests.get(
        f"https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={MW_THESAURUS_API_KEY}"
    )
    if response.status_code == 200:
        data = response.json()
        # TODO: Extract necessary info
        return data
    else:
        return None


def get_mv_dictionary_output(word: str) -> str | None:
    response = requests.get(
        f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={MW_DICTIONARY_API_KEY}"
    )
    if response.status_code == 200:
        data = response.json()
        return process_api_response_to_string(data)
    else:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(f"Hi {user.mention_html()}!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")


async def output_word_info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Given word as input, output information from Marriam-Webster sources"""
    word = update.message.text
    out = get_mv_dictionary_output(word)
    await update.message.reply_text(out)


bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, output_word_info)
)


@app.get("/")
async def root():
    """Root endpoint showing bot status."""
    return {
        "message": "🍓☁️ Telegram Bot running on Raspberry Pi via Cloudflare Tunnel!",
        "status": "active",
        "tunnel": "cloudflare",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "FastAPI + Cloudflare Tunnel",
        "timestamp": "2025-05-29",
    }


@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    try:
        if not bot_app.running:
            await bot_app.initialize()
            await bot_app.start()

        json_data = await request.json()
        update = Update.de_json(json_data, bot_app.bot)
        await bot_app.process_update(update)
        return {"status": "ok", "processed": True}
    except Exception as e:
        logger.error(f"Error with webhook processing: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", reload=False, port=8000, log_level="info")
