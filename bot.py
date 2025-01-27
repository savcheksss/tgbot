import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
    await update.message.reply_text("Привет! Я бот для предложки. Отправь сообщение, чтобы предложить его в канал.")

# Обработка предложений
async def handle_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    try:
        # Уведомление админу
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новое предложение от @{user.username or 'анонимного пользователя'}:\n{text}",
        )
        logger.info("Уведомление админу отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")

    try:
        # Отправка сообщения в канал
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"Предложение от @{user.username or 'анонимного пользователя'}:\n{text}",
        )
        await update.message.reply_text("Ваше предложение отправлено в канал.")
        logger.info("Сообщение успешно отправлено в канал")
    except Exception as e:
        logger.error(f"Ошибка при отправке в канал: {e}")
        await update.message.reply_text("Произошла ошибка при отправке сообщения в канал.")

# Тестовая команда для уведомлений
async def test_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text="Тестовое уведомление от бота!")
        await update.message.reply_text("Тестовое уведомление отправлено.")
        logger.info("Тестовое уведомление отправлено админу")
    except Exception as e:
        logger.error(f"Ошибка при отправке тестового уведомления: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

# Основная функция
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_notify))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proposal))

    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
