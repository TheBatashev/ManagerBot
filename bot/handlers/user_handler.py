from aiogram.types import Message, CallbackQuery, ChatJoinRequest, ChatMemberUpdated, FSInputFile
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import random
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from ..keyboards import create_captcha_kb, get_image_captcha
from ..filters import ChatTypeFilter
from ..states import UserState
from config import settings

from database import database as crud
from utils import redis_cache , captcha_worker

user_router = Router()

asyncio_queue = asyncio.Queue()

@user_router.message(F.text == "/start")
async def start(message: Message, session : AsyncSession, bot : Bot):
    user_id = message.from_user.id
    await crud.get_or_create_user(session, message.from_user.id, message.from_user.username)
        # await redis_cache.set(f'{user_id}', user_id, 60*60*24)
        
    await message.answer(f"<b>🔎 Здравствуй. Это твой личный охранник Guard Bot</b>")

# F.chat.type.in_(['group', 'supergroup']
# ChatTypeFilter(['group', 'supergroup', 'private']
@user_router.chat_member()
async def join_request(message: ChatMemberUpdated, session : AsyncSession, state: FSMContext, bot : Bot):
    if message.new_chat_member.status in ['member', 'administrator', 'creator']:
        user_id = message.new_chat_member.user.id
        chat_name = message.chat.full_name
        emoji = random.choice(settings.EMOJIS)
        get_photo_url = await get_image_captcha(emoji)
        photo = FSInputFile(get_photo_url)
        msg = await bot.send_photo(chat_id=message.chat.id, photo=photo ,caption=f"<b>🔎 Здравствуй. Ты попал в чат {chat_name}\n\nПожалуйста, пройди капчу ( у тебя 15 секунд )</b>", reply_markup=await create_captcha_kb(settings.EMOJIS, emoji, user_id))
        await redis_cache.set(f'{user_id}_captcha', 'active', 60*60)
        asyncio.create_task(captcha_worker(bot, redis_cache, f'{user_id}_captcha', message.chat.id, user_id, msg.message_id))

    if message.old_chat_member.status in ['member', 'administrator', 'creator']:
        username = message.old_chat_member.user.full_name
        await bot.send_message(chat_id=message.chat.id, text=f"Брат {username}, не покидай нас(.")

@user_router.callback_query(F.data.startswith('cap_'))
async def check_captcha(call: CallbackQuery, state : FSMContext, bot : Bot):
    user_id = int(call.from_user.id)

    data = call.data.split('_')
    color = data[1]
    user_id_data = int(data[2])
    captcha_color = data[3]

    if color == captcha_color and user_id_data == user_id:
        await redis_cache.delete(f'{user_id}_captcha')
        await call.message.delete()
    elif color != captcha_color and user_id_data == user_id:
        await call.answer('Неправильно!')
    elif color == captcha_color and user_id_data != user_id:
        await call.answer('Не твоя капча!')


@user_router.message()
async def messages_handler(message: Message, state : FSMContext):
    user_id = message.from_user.id
    captcha = await redis_cache.get(f'{user_id}_captcha')
    if captcha == 'active':
        await message.delete()
    else:
        pass