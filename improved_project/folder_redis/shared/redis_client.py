# shared/redis_client.py
import redis.asyncio as redisaio
import os
import json

class RedisClient:
    def __init__(self):
        self.redis = None
        self.prefix = ""  # for consistent key handling
        self.url = "redis://localhost:6379"

    async def connect(self):
        self.redis = await redisaio.from_url(
            self.url,
            decode_responses=True
        )

    def _key(self, task_id: str) -> str:
        return f"{self.prefix}{task_id}"

    async def set_status(self, task_id: str, status: str, result=None):
        await self.redis.set(self._key(task_id), json.dumps({
            "status": status,
            "result": result
        }))

    async def get(self, task_id: str):
        return await self.redis.get(self._key(task_id))

    async def delete(self, task_id: str):
        await self.redis.delete(self._key(task_id))

    async def aclose(self):
        await self.redis.aclose()
