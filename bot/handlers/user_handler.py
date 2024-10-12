from aiogram.types import Message, CallbackQuery
from aiogram import Router, F

from sqlalchemy.ext.asyncio import AsyncSession

from database import database as crud
from utils import redis_cache 

user_router = Router()

@user_router.message(F.text == "/start")
async def start(message: Message, session : AsyncSession):
    user_id = message.from_user.id
    if await redis_cache.get(f'{user_id}') is None:
        await crud.get_or_create_user(session, message.from_user.id, message.from_user.username)
        await redis_cache.set(f'{user_id}', user_id, 60*60*24)
        
    await message.answer(f"<b>🔎 Ассаламу алейкум")
