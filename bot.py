import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from flask import Flask, request

# Явно указываем переменные окружения
TELEGRAM_TOKEN = "7259551368:AAEpMtdGtEbOvuXhEry4TRGJqnz7-h5TYFk"
CHANNEL_ID = "-1002401365916"
ADMIN_ID = "879236410"
WEBHOOK_URL = "https://tgbot-urib0f1bn-savcheksss-projects.vercel.app/webhook"

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Создаем приложение
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Flask-приложение для обработки webhook
app = Flask(__name__)

# Команда /start для приветствия
async def start(update: Update, context):
    """Команда /start"""
    await update.message.reply_text("Привет! Я бот предложки. Отправь предложение и я передам его администратору.")

# Обработчик предложений от пользователей
async def handle_proposal(update: Update, context):
    """Обработка предложений от пользователей"""
    user = update.effective_user
    text = update.message.text

    if update.message.photo:
        # Если пришло фото
        photo = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=f"Новое предложение от @{user.username or 'без имени'}:\n{text or 'Без текста'}",
            reply_markup=InlineKeyboardMarkup([ 
                [InlineKeyboardButton("✅ Принять", callback_data=f"accept:{photo.file_id}:{text or ''}")],
                [InlineKeyboardButton("❌ Отклонить", callback_data="reject")],
            ]),
        )
    else:
        # Если пришел текст
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новое предложение от @{user.username or 'без имени'}:\n{text}",
            reply_markup=InlineKeyboardMarkup([ 
                [InlineKeyboardButton("✅ Принять", callback_data=f"accept:::{text}")],
                [InlineKeyboardButton("❌ Отклонить", callback_data="reject")],
            ]),
        )

# Обработчик колбэков кнопок "Принять" и "Отклонить"
async def handle_callback(update: Update, context):
    """Обработка кнопок принятия или отклонения предложений"""
    query = update.callback_query
    data = query.data

    if data.startswith("accept"):
        # Разбор данных из callback
        _, file_id, caption = data.split(":", maxsplit=2)
        if file_id:
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=caption)
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=caption)
        await query.answer("Сообщение опубликовано!")
    elif data == "reject":
        await query.answer("Сообщение отклонено!")
    await query.message.delete()

# Flask обработка вебхука
@app.route("/webhook", methods=["POST"])
def webhook():
    """Обрабатывает POST-запросы от Telegram"""
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is running"

# Установка webhook
async def set_webhook():
    """Устанавливаем webhook для обработки запросов от Telegram"""
    webhook_url = os.getenv("WEBHOOK_URL")
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook успешно установлен на {webhook_url}")

if __name__ == "__main__":
    # Устанавливаем webhook и запускаем Flask
    application.updater.start_polling()
    app.run(debug=True)
