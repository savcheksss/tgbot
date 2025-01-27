import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext

# Чтение токена и ID из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = 879236410  # Твой ID для получения уведомлений

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для предложки канала. Отправь сообщение, и я передам его на модерацию.")

def handle_proposal(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text

    # Кнопки для одобрения/отклонения
    keyboard = [
        [InlineKeyboardButton("Одобрить", callback_data=f"approve:{user.id}:{text}"),
         InlineKeyboardButton("Отклонить", callback_data=f"reject:{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправка сообщения администратору (тебе)
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новое предложение от @{user.username or 'анонимного пользователя'}:\n{text}",
        reply_markup=reply_markup
    )

    # Уведомление пользователю
    update.message.reply_text("Ваше предложение отправлено на модерацию.")

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split(":")
    action = data[0]

    if action == "approve":
        text = ":".join(data[2:])
        context.bot.send_message(chat_id=CHANNEL_ID, text=f"Предложение:\n{text}")
        query.edit_message_text("Предложение одобрено и отправлено в канал.")
    elif action == "reject":
        query.edit_message_text("Предложение отклонено.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики команд и сообщений
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_proposal))
    dp.add_handler(CallbackQueryHandler(handle_callback))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
