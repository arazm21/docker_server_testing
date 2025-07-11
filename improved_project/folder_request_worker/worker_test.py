import asyncio
import aio_pika
import redis.asyncio as redisaio
import json
import os
import time
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv("../.env")

REDIS_URL = "redis://localhost:6379"
AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
REQUEST_QUEUE = os.getenv("REQUEST_QUEUE", "predict_request")

print(REDIS_URL)
async def main():
    # Step 1: Connect to Redis
    
    redis = await redisaio.from_url(REDIS_URL, decode_responses=True)
    print("redis con")
    # Step 2: Connect to RabbitMQ
    try:
        connection = await aio_pika.connect_robust(AMQP_URL)
        channel = await connection.channel()
        await channel.declare_queue(REQUEST_QUEUE, durable=True)
        print("rabbit connection")
    except Exception as e:
        print(f"❌ Failed to connect to RabbitMQ: {e}")
        return

    # Step 3: Submit task to queue
    task_id = str(uuid4())
    payload = {
        "task_id": task_id,
        "wine_id": 1,
        "real_time_measurement": 6.7
    }

    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(payload).encode()),
        routing_key=REQUEST_QUEUE
    )
    print(f"📤 Sent task {task_id} to `{REQUEST_QUEUE}`")

    # Step 4: Watch Redis for status updates
    redis_key = f"{task_id}"
    for i in range(20):
        val = await redis.get(redis_key)
        if val:
            parsed = json.loads(val)
            print(f"[{i}] status: {parsed['status']}")
            if parsed["status"] in ["DONE", "ERROR"]:
                print(f"✅ Final result: {parsed['result']}")
                break
        else:
            print(f"[{i}] Waiting for task to appear in Redis...")
        await asyncio.sleep(1)
    else:
        print("⚠️ Timeout: task did not complete in expected time")

    await redis.aclose()
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
