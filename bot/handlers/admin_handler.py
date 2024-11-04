from aiogram.types import Message, CallbackQuery
from aiogram import Router, F

from sqlalchemy.ext.asyncio import AsyncSession

from database import database as crud
from utils import redis_cache 

admin_router = Router()