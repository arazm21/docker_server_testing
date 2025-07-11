import aioredis
import json
import os

class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def set_status(self, task_id, status, result=None):
        await self.redis.set(
            f"{task_id}",
            json.dumps({"status": status, "result": result})
        )
