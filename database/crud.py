from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, ScalarResult

from typing import Union, List
from datetime import datetime, timedelta

from .models import User, Level, Category, LastWord, Word

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
        

    async def get_user(self, session: AsyncSession, user_id):
        async with session.begin() :
            user = await session.execute(select(User.id).where(User.user_id == user_id))
            user_ =  user.scalar_one_or_none()

            return user_
    

    async def get_users_with_last_words(self, session: AsyncSession) :
        """
        Получаем юзеров и их последние слова

        Пример выходных данных: [('Юзер Ид', 'Категория_ИД', 'Слово_ИД', 'Категория_ИМЯ','Слово_ИМЯ')]

        """
        current_time = datetime.now()  # Получаем текущее время в формате UTC
        results = await session.execute(
            select(
                User.user_id,
                Category.id.label('category_id'),  # Добавляем ID категории
                Word.id.label('word_id'),           # Добавляем ID слова
                Category.name.label('category_name'),
                Word.word.label('last_word')
            ).distinct()
            .join(LastWord, User.id == LastWord.user_id)
            .join(Category, LastWord.category_id == Category.id)
            .join(Word, LastWord.word_id == Word.id)
            # .where(User.subscription_end_date >= current_time)  # Проверяем, что подписка активна
            .where(User.category_id == Category.id)  # Эта строка не нужна, так как связи уже установлены
        )
        
        # Получаем все результаты, если необходимо
        return results.all()


    async def get_premium_users(self, session: AsyncSession):
        """
        Получаем всех юзеров с активной подпиской
        """
        # async with session.begin() :
        users_all = await session.execute(select(User.user_id).where(User.subscription_end_date > datetime.now()))
        users =  users_all.scalars().all()

        return users
        


    async def get_user_last_word(self, session: AsyncSession, user_id, cat_id):
        """
        Получаем ласт слово юзера по категории
        """
        async with session.begin() :
            user_last_word = await session.execute(select(LastWord.word_id).where(LastWord.user_id == user_id, LastWord.category_id == cat_id))
            user_last_word_id = user_last_word.scalar_one_or_none()
            # print(f'user_last_word_id: {user_last_word_id}')
            return user_last_word_id


    async def update_last_word(self, session: AsyncSession, user_id, word_id, category_id):
        """
        Обновляем последнее слово юзера из определенной категории
        """
        words = await session.execute(select(Word.id).where(Word.category_id == category_id).order_by(Word.id))
        next_word_id = None
        for word in words.scalars().all():
            if word.id > word_id:
                next_word_id = word.id

        if next_word_id is not None:
            async with session.begin():
                stmt = (
                    update(LastWord).
                    where(LastWord.user_id == user_id, LastWord.category_id == category_id).
                    values(word_id=next_word_id)
                )
                await session.execute(stmt)
                await session.commit()

    async def set_user_last_word(self, session: AsyncSession, user_id, category_id):
        """
        Добавляем последнее слово юзера из определенной категории
        """
        async with session.begin():
            word_id_ = await session.execute(
                select(Word.id)
                .where(Word.category_id == category_id)
                .order_by(Word.id.asc()) )
            
            word_id = word_id_.scalars().first()

            if word_id is not None:
                stmt = (
                    insert(LastWord).
                    values(user_id=user_id, category_id=category_id, word_id=word_id)
                )
                await session.execute(stmt)
                await session.commit()

    async def set_subscription(self, session, month, user_id):
        """
        Обновляем подписку
        """
        subscription_end_date = datetime.now() + timedelta(days=month * 30)
        # async with session.begin():
        await session.execute(update(User).where(User.user_id == user_id).values(subscription_end_date=subscription_end_date))
        await session.commit()

    async def get_subscription(self, session: AsyncSession, user_id):
        async with session.begin() :
            user = await session.execute(select(User.subscription_end_date).where(User.user_id == user_id))
            user_ =  user.scalar_one_or_none()

            return user_
        
    async def get_premiums_inactive(self, session: AsyncSession):
        """
        Получаем всех юзеров у которых до окончания подписки осталось 1
        """
        users_1_day = await session.execute(select(User.user_id).where(User.subscription_end_date - datetime.now() <= timedelta(days=1)))
        users_3_day = await session.execute(select(User.user_id).where(User.subscription_end_date - datetime.now() <= timedelta(days=3)))
        users_7_day = await session.execute(select(User.user_id).where(User.subscription_end_date - datetime.now() <= timedelta(days=7)))

        return {'day': users_1_day.scalars().all(), '3day': users_3_day.scalars().all(), 'week': users_7_day.scalars().all()}

class CategoryLevelDb :

    async def get_level(self, session: AsyncSession, level_name):
        async with session.begin() :
            level = await session.execute(select(Level.id).where(Level.level_name == level_name))
            level_ =  level.scalar_one_or_none()
            print(f'{level} || Level')
            return level_
        

    async def get_categories(self, session: AsyncSession, level):
        async with session.begin() :
            categories_all = await session.execute(select(Category.name).where(Category.level_id == level))
            categories =  categories_all.scalars().all()
            print(categories)

            return categories
    
    async def get_category(self, session: AsyncSession, category):
        async with session.begin() :
            category = await session.execute(select(Category.id).where(Category.name == category))
            category_ =  category.scalar_one_or_none()
            # print(f'{category} || Category')
            return category_

    async def set_level_user(self, session: AsyncSession, user_id, level_id):
        async with session.begin():
            stmt = (
                update(User).
                where(User.user_id == user_id).
                values(level_id=level_id)
            )
            await session.execute(stmt)
            await session.commit()
        
    async def set_category_user(self, session: AsyncSession, user_id, category_id):
        async with session.begin():
            stmt = (
                update(User).
                where(User.user_id == user_id).
                values(category_id=category_id)
            )
            await session.execute(stmt)
            await session.commit()
            return True
        
    async def get_category_user(self, session: AsyncSession, user_id):
        async with session.begin() :
            category = await session.execute(select(User.category_id).where(User.user_id == user_id))
            category_ =  category.scalar_one_or_none()
            return category_
        


class Database(UserDB, CategoryLevelDb) :
    pass


database = Database()