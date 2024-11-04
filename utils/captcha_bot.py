import asyncio
# asyncio_queue = asyncio.Queue()

async def captcha_worker(bot, redis, key, chat_id, user_id, msg_id):
    await asyncio.sleep(15)
    captcha = await redis.get(key)
    if captcha == 'active':
        await redis.delete(key)
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    else:
        return True

# asyncio.create_task(db_worker())
