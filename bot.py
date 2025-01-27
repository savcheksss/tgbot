import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_webhook

# Логирование
logging.basicConfig(level=logging.INFO)

# ==================
# ПЕРЕМЕННЫЕ
# ==================
TOKEN = "7259551368:AAEpMtdGtEbOvuXhEry4TRGJqnz7-h5TYFk"  # Токен вашего бота
ADMIN_CHANNEL_ID = -1002292572104  # ID админского канала
PUBLISHED_CHANNEL_ID = -1001234567890  # ID канала для публикации (замените на реальный ID)

WEBHOOK_PATH = f"/webhook/{TOKEN}"  # Путь для Webhook
WEBHOOK_URL = f"https://572de7e7-9c6f-4eb0-9694-7cdb9460a16f.up.railway.app{WEBHOOK_PATH}"  # URL для Webhook
WEBAPP_HOST = "0.0.0.0"  # Хост для Railway
WEBAPP_PORT = 5000  # Порт для Railway

# ==================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ==================
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# ==================
# ОБРАБОТКА ФОТО
# ==================
@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    # Получаем фото максимального размера
    photo = message.photo[-1]
    caption = f"Пост от {message.from_user.full_name}"

    # Создаём клавиатуру с кнопками "Опубликовать" и "Отменить"
    keyboard = InlineKeyboardMarkup(row_width=2)
    publish_button = InlineKeyboardButton("Опубликовать", callback_data="publish")
    cancel_button = InlineKeyboardButton("Отменить", callback_data="cancel")
    keyboard.add(publish_button, cancel_button)

    # Отправляем фото в админский канал с кнопками
    await bot.send_photo(
        chat_id=ADMIN_CHANNEL_ID,
        photo=photo.file_id,
        caption=caption,
        reply_markup=keyboard,
    )


# ==================
# ОБРАБОТКА КНОПОК
# ==================
@dp.callback_query_handler(lambda callback_query: True)
async def handle_callback_query(callback_query: types.CallbackQuery):
    if callback_query.data == "publish":
        # Обработка публикации
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Пост опубликован в канале.",
        )
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )

        # Отправка фото в канал
        photo_message = callback_query.message.reply_to_message
        photo = photo_message.photo[-1]
        caption = photo_message.caption if photo_message.caption else None
        await bot.send_photo(
            chat_id=PUBLISHED_CHANNEL_ID,
            photo=photo.file_id,
            caption=caption,
        )

    elif callback_query.data == "cancel":
        # Обработка отмены
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Публикация отменена.",
        )
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )


# ==================
# НАСТРОЙКА WEBHOOK
# ==================
async def on_startup(dp):
    logging.info("Установка Webhook...")
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.info("Удаление Webhook...")
    await bot.delete_webhook()
    await bot.close()


# ==================
# ЗАПУСК БОТА
# ==================
if __name__ == "__main__":
    from aiogram import executor

    logging.info("Запуск бота...")
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
