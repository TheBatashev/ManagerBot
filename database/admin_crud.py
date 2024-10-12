from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, ScalarResult, func, case


from typing import Union, List
from datetime import datetime, timedelta

from .models import User, Level, Category

from .crud import Database


class AdminDatabase(Database):

    async def get_users_count_all(self, session: AsyncSession):
        async with session.begin():
            users_all = await session.execute(select(User.user_id))
            users =  users_all.all()

            return len(users)
        
    
    async def get_users_count_last(self, session: AsyncSession):
        """
        Получаем новых пользователей бота за последние: день, неделю, месяц
        """
        async with session.begin():

            # Создаем условные выражения для подсчета пользователей за разные промежутки времени
            users_month = await session.execute(select(func.count(User.user_id)).where(User.created_at >= datetime.now() - timedelta(days=30)))
            users_week = await session.execute(select(func.count(User.user_id)).where(User.created_at >= datetime.now() - timedelta(days=7)))
            users_day = await session.execute(select(func.count(User.user_id)).where(User.created_at >= datetime.now() - timedelta(days=1)))
            return {'month': users_month.scalar_one(), 'week': users_week.scalar_one(), 'day': users_day.scalar_one()}


admin_database = AdminDatabase()