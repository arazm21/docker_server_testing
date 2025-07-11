import asyncio
from fastapi import FastAPI, HTTPException
from shared.redis_client import RedisClient
import json
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
redis_client = RedisClient()


@app.on_event("startup")
async def startup():
    await redis_client.connect()


@app.on_event("shutdown")
async def shutdown():
    await redis_client.aclose()


@app.get("/items")
async def list_items():
    keys = await redis_client.redis.keys("*")
    items = {}
    for key in keys:
        value = await redis_client.redis.get(key)
        try:
            items[key] = json.loads(value)
        except:
            items[key] = value
    return items

 
@app.delete("/items/{task_id}")
async def delete_item(task_id: str):
    result = await redis_client.delete(task_id)
    if result == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": f"Deleted task {task_id}"}

@app.delete("/clear")
async def clear_all_items():
    result = await redis_client.redis.flushdb()
    logging.info(f"fulsh result : {result}")
    return {"detail": "All items cleared from Redis "}

# uvicorn redis_api:app --reload --port 6001