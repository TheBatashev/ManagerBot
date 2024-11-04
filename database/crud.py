from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, ScalarResult

from typing import Union, List
from datetime import datetime, timedelta

from .models import User

from typing import List


# User queries

class UserDB : 
    

    async def get_or_create_user(self, session: AsyncSession, user_id: int, username: str) -> User:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user: User = result.scalar_one_or_none()

            if user is None:
                user = User(
                    user_id=user_id,
                    username=username,
                )
                await session.merge(user)

            await session.commit()

            return user

    async def get_users(self, session: AsyncSession):
        async with session.begin() :
            users_all = await session.execute(select(User.user_id))
            users =  users_all.scalars().all()

            return users


class Database(UserDB) :
    pass


database = Database()