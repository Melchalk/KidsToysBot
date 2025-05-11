import logging
import os
import tempfile
from gtts import gTTS
from telegram import Update
from telegram.ext import ContextTypes
import speech_recognition as sr
from bot_logic.handler import bot, get_passive_hint
from pydub import AudioSegment

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.message.from_user.id} started the bot")
    intent_answer = bot("что ты умеешь")
    await update.message.reply_text(f"Привет! Я бот магазина игрушек\n{intent_answer}")
    schedule_passive_hint(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.message.from_user.id} asked for help")
    await update.message.reply_text("Я могу поболтать с вами и посоветовать игрушки 😊")

async def send_passive_hint(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    hint = get_passive_hint()
    await context.bot.send_message(chat_id=chat_id, text=hint)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logger.info(f"User {update.message.from_user.id} said: {user_input}")
    response = bot(user_input)
    logger.info(f"Response for user: {response}")
    await update.message.reply_text(response)
    schedule_passive_hint(update, context)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await voice.get_file()

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        await file.download_to_drive(f.name)
        ogg_path = f.name

    wav_path = ogg_path.replace('.ogg', '.wav')
    AudioSegment.from_ogg(ogg_path).export(wav_path, format='wav')

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio, language='ru-RU')
        except sr.UnknownValueError:
            recognized_text = None

    os.remove(ogg_path)
    os.remove(wav_path)

    if not recognized_text:
        await update.message.reply_text("Извините, не смог распознать речь")
        return

    await update.message.reply_text(f"Вы сказали: {recognized_text}")
    answer = bot(recognized_text)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tts = gTTS(answer, lang='ru', slow=True)
        tts.save(f.name)
        voice_path = f.name

    await update.message.reply_voice(voice=open(voice_path, "rb"))
    os.remove(voice_path)
    schedule_passive_hint(update, context)

def schedule_passive_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if context.chat_data.get("passive_job"):
        context.chat_data["passive_job"].schedule_removal()

    job = context.job_queue.run_once(send_passive_hint, int(os.getenv("DELAY_HINT")), chat_id=chat_id)
    context.chat_data["passive_job"] = job