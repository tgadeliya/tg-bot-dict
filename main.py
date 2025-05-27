import os

import requests 
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from dictionaries import process_api_response_to_string

load_dotenv()
TELEGRAM_BOT_TOKEN: str| None = os.getenv("TELEGRAM_BOT_TOKEN")
MW_THESAURUS_API_KEY: str | None = os.getenv("MW_THESAURUS_KEY")
MW_DICTIONARY_API_KEY: str | None = os.getenv("MW_DICTIONARY_KEY")

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
    await update.message.reply_html(
        f"Hi {user.mention_html()}!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

async def output_word_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Given word as input, output information from Marriam-Webster sources"""
    word = update.message.text
    out = get_mv_dictionary_output(word)
    await update.message.reply_text(out)

def main():
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
 
    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, output_word_info))
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    

if __name__ == "__main__":
    main()