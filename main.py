import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from sqlalchemy.ext.asyncio import AsyncSession


from bot import DbSessionMiddleware, user_router, admin_router
from database import get_session_maker, create_engine, init_models

from config import settings


async def on_shutdown(dp: Dispatcher):
    session: AsyncSession = dp.update.middleware['session']



async def start():
    bot = Bot(token=settings.BOT_TOKEN  , default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        admin_router, user_router
    )

    async_engine = create_engine()
    session_maker = get_session_maker(async_engine)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    logging.basicConfig(filename='logs/bot.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    me = await bot.get_me()
    print('Started')
    print(me.username)

    try:
        # await init_models()
        # run_check_exchanges_status(session_maker, bot)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
