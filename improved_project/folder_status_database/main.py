import aioredis
import json

class RedisClient:
    def __init__(self, url="redis://localhost"):
        self.redis_url = url
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def set_status(self, task_id, status, result=None):
        data = {"status": status, "result": result}
        await self.redis.set(f"{task_id}", json.dumps(data))

    async def get_status(self, task_id):
        raw = await self.redis.get(f"{task_id}")
        if raw:
            return json.loads(raw)
        return None
