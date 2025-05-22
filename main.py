import logging
import os
import tempfile
from dotenv import load_dotenv
from gtts import gTTS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import speech_recognition as sr
from bot_logic.bot import bot
from bot_logic.dialog import structure_dialogues
from pydub import AudioSegment
from bot_logic.handlers import start, help_command, handle_message, handle_voice

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("Не задан токен Telegram-бота! Установите переменную TELEGRAM_BOT_TOKEN.")

def main():
    structure_dialogues()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    job_queue = app.job_queue

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()

if __name__ == '__main__':
    main()
