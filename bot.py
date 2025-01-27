import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Чтение токена и ID из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = 879236410  # Твой ID для уведомлений

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для предложки канала. Отправь сообщение, и я передам его на модерацию.")

async def handle_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # Кнопки для модерации
    keyboard = [
        [
            InlineKeyboardButton("Одобрить", callback_data=f"approve:{user.id}:{text}"),
            InlineKeyboardButton("Отклонить", callback_data=f"reject:{user.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Уведомление админу (тебе)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новое предложение от @{user.username or 'анонимного пользователя'}:\n{text}",
        reply_markup=reply_markup,
    )

    # Уведомление пользователю
    await update.message.reply_text("Ваше предложение отправлено на модерацию.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(":")
    action = data[0]

    if action == "approve":
        text = ":".join(data[2:])
        await context.bot.send_message(chat_id=CHANNEL_ID, text=f"Предложение:\n{text}")
        await query.edit_message_text("Предложение одобрено и отправлено в канал.")
    elif action == "reject":
        await query.edit_message_text("Предложение отклонено.")

def main():
    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proposal))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
