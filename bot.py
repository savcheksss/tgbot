import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Установите токен вашего бота
TOKEN = '7259551368:AAEpMtdGtEbOvuXhEry4TRGJqnz7-h5TYFk'  # Замени на свой токен

# Установите ID вашего админского канала
ADMIN_CHANNEL_ID = '-1002292572104'  # Твой админский канал

# Установите ID канала, в который нужно отправить фото
PUBLISHED_CHANNEL_ID = '@toskvabrk'  # Канал, куда будет отправляться пост

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Настройка логирования
logging.basicConfig(level=logging.INFO)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # Получаем последнюю (наибольшую) фотографию из списка
    caption = f'Пост от {message.from_user.full_name}'

    # Создаем клавиатуру с кнопками "Опубликовать" и "Отменить"
    keyboard = InlineKeyboardMarkup(row_width=2)
    publish_button = InlineKeyboardButton('Опубликовать', callback_data='publish')
    cancel_button = InlineKeyboardButton('Отменить', callback_data='cancel')
    keyboard.add(publish_button, cancel_button)

    # Отправляем фото в админский канал с клавиатурой
    await bot.send_photo(chat_id=ADMIN_CHANNEL_ID, photo=photo.file_id, caption=caption, reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: True)
async def handle_callback_query(callback_query: types.CallbackQuery):
    if callback_query.data == 'publish':
        # Ответ на нажатие кнопки "Опубликовать"
        await bot.send_message(chat_id=callback_query.from_user.id, text='Пост опубликован в канале.')
        await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id)
        # Отправляем фото в целевой канал
        photo_message = callback_query.message.reply_to_message
        photo = callback_query.message.photo[-1]
        caption = callback_query.message.caption if hasattr(callback_query.message, 'caption') else None
        await bot.send_photo(chat_id=PUBLISHED_CHANNEL_ID, photo=photo.file_id, caption=caption)

    elif callback_query.data == 'cancel':
        # Ответ на нажатие кнопки "Отменить"
        await bot.send_message(chat_id=callback_query.from_user.id, text='Отмена.')
        await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id)

# Запуск бота
async def main():
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()

if __name__ == '__main__':
    # Запуск бота
    logging.info('Starting bot...')
    asyncio.run(main())
