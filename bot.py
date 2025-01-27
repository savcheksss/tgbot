import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import asyncio
from telegram.error import RetryAfter

# Переменные окружения
TOKEN = "7849762948:AAHCcSOsTf-awCH2E99IJZFR0dW56AWulPk"  # Токен вашего бота
CHANNEL_ID = -1002401365916  # ID канала
ADMIN_ID = 879236410  # ID администратора
WEBHOOK_URL = "https://tgbot-rho-nine.vercel.app/webhook"  # URL для webhook

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context):
    """Команда /start"""
    await update.message.reply_text("Привет! Я бот предложки.")

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

# Главная функция для создания приложения
def create_app():
    """Создание и настройка приложения Telegram Bot"""
    app = Application.builder().token(TOKEN).build()

    # Установка обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_proposal))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Функция для установки webhook с обработкой ошибок
    async def set_webhook():
        """Настройка webhook с обработкой ошибок Flood control"""
        try:
            await app.bot.set_webhook(WEBHOOK_URL)
            logger.info("Webhook успешно установлен.")
        except RetryAfter as e:
            logger.warning(f"Превышен лимит запросов, повторим через {e.retry_after} секунд.")
            await asyncio.sleep(e.retry_after)  # Ожидание перед повтором
            await set_webhook()  # Повторная попытка установки webhook
        except Exception as e:
            logger.error(f"Ошибка при установке webhook: {e}")

    # Асинхронно запускаем установку webhook через create_task
    asyncio.create_task(set_webhook())

    return app

# Определяем переменную handler для Vercel
handler = create_app()
