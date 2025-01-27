import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# Токен и ID
TELEGRAM_TOKEN = "7849762948:AAHCcSOsTf-awCH2E99IJZFR0dW56AWulPk"
CHANNEL_ID = "-1002401365916"
ADMIN_ID = 879236410  # Твой ID для уведомлений

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для предложки. Отправь сообщение или картинку, чтобы предложить его в канал. "
        "Администратор подтвердит или отклонит ваш запрос."
    )

# Обработка предложений (текст и изображения)
async def handle_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    # Создаём inline-кнопки
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve|{chat_id}|{message_id}"),
            InlineKeyboardButton("🖕 Иди нахуй", callback_data=f"reject|{chat_id}|{message_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Если сообщение содержит текст
    if update.message.text:
        text = update.message.text
        # Отправка админу для подтверждения
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новое предложение от @{user.username or 'анонимного пользователя'}:\n{text}",
            reply_markup=reply_markup,
        )
    # Если сообщение содержит фото
    elif update.message.photo:
        caption = update.message.caption or "Без подписи"
        file_id = update.message.photo[-1].file_id  # Берём самое большое изображение
        # Отправка изображения админу для подтверждения
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=f"Новое предложение от @{user.username or 'анонимного пользователя'}:\n{caption}",
            reply_markup=reply_markup,
        )

    # Подтверждение отправителю
    await update.message.reply_text("Ваше предложение отправлено на модерацию.")

# Обработка нажатий на inline-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Уведомление Telegram, что запрос обработан

    # Парсим данные из callback_data
    action, chat_id, message_id = query.data.split("|")

    if action == "approve":
        # Отправляем сообщение в канал
        try:
            # Перенаправляем текст или фото из исходного сообщения
            original_message = await context.bot.forward_message(
                chat_id=int(CHANNEL_ID),
                from_chat_id=int(chat_id),
                message_id=int(message_id),
            )
            await query.edit_message_text("Сообщение успешно опубликовано в канал.")
            logger.info(f"Сообщение опубликовано: {original_message.message_id}")
        except Exception as e:
            logger.error(f"Ошибка при публикации: {e}")
            await query.edit_message_text("Ошибка при публикации сообщения.")
    elif action == "reject":
        # Уведомление об отклонении
        await query.edit_message_text("Сообщение отклонено: Иди нахуй.")
        # Сообщаем пользователю, что его сообщение отклонено
        try:
            await context.bot.send_message(
                chat_id=int(chat_id),
                text="К сожалению, ваше предложение было отклонено администратором. Иди нахуй.",
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления об отклонении: {e}")

# Основная функция
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_proposal))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
