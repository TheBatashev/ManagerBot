import redis
import json

from config import settings

from datetime import datetime


async def get_instance(json_value):
        if isinstance(json_value, str) or isinstance(json_value, datetime) or isinstance(json_value, int) or isinstance(json_value, float):
            return True


class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=db)

    async def set(self, key, value, ex=settings.REDIS_EXPIRE):
        # Сериализация значения в JSON, сохраняя datetime объекты как строки
        serialized_value = json.dumps(await self.serialize(value))
        self.client.set(key, serialized_value, ex=ex)

    async def get(self, key):
        value = self.client.get(key)
        if value is not None:
            return await self.deserialize(json.loads(value))
        return None


    async def delete(self, key):
        try:
            self.client.delete(key)
            return key
        except redis.RedisError:
            pass


    async def serialize(self, obj):
        """Рекурсивно сериализует объекты, преобразуя datetime в строки."""
        if isinstance(obj, dict):
            return {key: await self.serialize(val) for key, val in obj.items()}
        elif isinstance(obj, list):
            return [await self.serialize(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Преобразуем datetime в строку
        return obj  # Возвращаем объект, если он не datetime и не коллекция


    async def deserialize(self, obj):
        """Рекурсивно десериализует объекты, преобразуя строки обратно в datetime."""
        if isinstance(obj, dict):
            return {key: await self.deserialize(val) for key, val in obj.items()}
        elif isinstance(obj, list):
            return [await self.deserialize(item) for item in obj]
        elif isinstance(obj, str):
            try:
                return datetime.fromisoformat(obj)  # Преобразуем строку обратно в datetime
            except ValueError:
                return obj  # Возвращаем строку, если преобразование не удалось
        return obj  




redis_cache = RedisCache()
