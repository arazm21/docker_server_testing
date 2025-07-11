import asyncio
import aio_pika
import redis.asyncio as redisaio
import json
import os
from uuid import uuid4
from dotenv import load_dotenv
import time

load_dotenv("../.env")

REDIS_URL = "redis://localhost:6379"
AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
RESPONSE_QUEUE = os.getenv("RESPONSE_QUEUE", "predict_response")

async def main():
    task_id = str(uuid4())

    # Step 1: Connect to Redis and set status to PENDING
    redis = await redisaio.from_url(REDIS_URL, decode_responses=True)
    await redis.set(task_id, json.dumps({"status": "PENDING", "result": None}))
    print(f"📝 Redis set {task_id} to PENDING")

    # Step 2: Connect to RabbitMQ and send task_id to shared queue
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    exchange = channel.default_exchange

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps({"task_id": task_id}).encode(),
            reply_to=f"{task_id}",
            correlation_id=task_id

        ),
        routing_key=RESPONSE_QUEUE
    )
    print("📤 Sent response check 1 (should return PENDING)")

    # Step 3: Wait and simulate DONE update
    await asyncio.sleep(2)

    await redis.set(task_id, json.dumps({
        "status": "DONE",
        "result": {"predicted_quality": 7.5}
    }))
    print(f"✅ Redis updated {task_id} to DONE")

    # Step 4: Send another response request
    await exchange.publish(
        aio_pika.Message(
            body=json.dumps({"task_id": task_id}).encode()
        ),
        routing_key=RESPONSE_QUEUE
    )
    print("📤 Sent response check 2 (should return DONE and delete task)")

    # Step 5: Wait for Redis to delete
    for i in range(10):
        await asyncio.sleep(1)
        val = await redis.get(task_id)
        if val is None:
            print(f"🧹 Redis cleanup check: ✅ task:{task_id} deleted")
            break
        else:
            print(f"⏳ Waiting for task:{task_id} to be deleted...")
    else:
        print(f"❌ Redis key {task_id} was not deleted")

    await redis.aclose()
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
