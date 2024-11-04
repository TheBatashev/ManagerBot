import random
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_image_captcha(color):
    if color == '🟦': return f'media/blue.jpg'
    if color == '🟨': return f'media/yellow.jpg'
    if color == '🟪': return f'media/purple.jpg'
    if color == '🟩': return f'media/green.jpg'
    if color == '🟥': return f'media/red.jpg'
    if color == '🟧': return f'media/orange.jpg'
    if color == '🟫': return f'media/brown.jpg'
    if color == '⬜️': return f'media/white.jpg'
    if color == '⬛️': return f'media/black.jpg'

#Создаем кнопки (по старинке простите)
async def create_captcha_kb(emojis, captcha, user_id):
    keyboard = InlineKeyboardBuilder()   
    random.shuffle(emojis)
    for item in emojis:
        keyboard.add(InlineKeyboardButton(text=item, callback_data=f'cap_{item}_{user_id}_{captcha}'))
    keyboard.adjust(3)
    return keyboard.as_markup()

