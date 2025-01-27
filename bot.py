import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

TOKEN = "7849762948:AAHCcSOsTf-awCH2E99IJZFR0dW56AWulPk"
CHANNEL_ID = -1002401365916
ADMIN_ID = 879236410
WEBHOOK_URL = "https://tgbot-c0ud.onrender.com/webhook"  # Обновили на новый URL

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот предложки.")

async def handle_proposal(update: Update, context):
    user = update.effective_user
    text = update.message.text

    if update.message.photo:
        # Если пользователь отправил фото
        photo = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=f"Новое предложение от @{user.username or 'без имени'}:\n{text or 'Без текста'}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Принять", callback_data=f"accept:{photo.file_id}:{text or ''}")],
                [InlineKeyboardButton("❌ Иди нахуй", callback_data="reject")],
            ]),
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новое предложение от @{user.username or 'без имени'}:\n{text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Принять", callback_data=f"accept:::{text}")],
                [InlineKeyboardButton("❌ Иди нахуй", callback_data="reject")],
            ]),
        )

async def handle_callback(update: Update, context):
    query = update.callback_query
    data = query.data

    if data.startswith("accept"):
        _, file_id, caption = data.split(":")
        await context.bot.send_message(chat_id=CHANNEL_ID, text=caption)
        await query.answer("Сообщение опубликовано!")
    elif data == "reject":
        await query.answer("Сообщение отклонено!")
    await query.message.delete()

def main():
    app = Application.builder().token(TOKEN).build()

    # Установка webhook
    app.bot.set_webhook(WEBHOOK_URL)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_proposal))
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Бот запущен...")
    
    # Запуск приложения на Render с вебхуком
    app.run_webhook(
        listen="0.0.0.0",
        port=80,  # Используем стандартный HTTP порт
        url_path="webhook",
    )

if __name__ == "__main__":
    main()
