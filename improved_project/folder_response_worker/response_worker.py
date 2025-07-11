import asyncio
import aio_pika
import json
import os
import logging
from dotenv import load_dotenv

from shared.redis_client import RedisClient

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Logging
logging.basicConfig(level=logging.INFO)

# RabbitMQ config
AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
RESPONSE_QUEUE = os.getenv("RESPONSE_QUEUE", "predict_response")

# Shared clients
redis_client = RedisClient()
exchange = None


async def on_response_request(message: aio_pika.IncomingMessage):
    logging.info(f"started working on response")
    global exchange
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            task_id = payload["task_id"]
            logging.info(f"📨 Received response request for task: {task_id}")

            # Fetch status/result from Redis
            redis_data = await redis_client.get(f"{task_id}")
            logging.info(f"got from redis: {redis_data}")    
            
            if redis_data is None:
                response = {"status": "NOT_FOUND"}
            else:
                parsed = json.loads(redis_data)
                status = parsed.get("status")
                result = parsed.get("result")

                response = {"status": status}
                if result is not None:
                    response["result"] = result

                # Cleanup if terminal state
                if status in ["DONE", "ERROR"]:
                    await redis_client.delete(f"{task_id}")
                    logging.info(f"🗑️ Deleted task {task_id} from Redis")

            # Send reply
            if message.reply_to:
                reply = aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=message.correlation_id
                )
                await exchange.publish(reply, routing_key=message.reply_to)
                logging.info(f"📤 Replied to {message.reply_to} for task {task_id}")
            else:
                logging.warning(f"⚠️ No reply_to set for task {task_id}, skipping reply.")


        except Exception as e:
            logging.exception("❌ Failed to process response request")


async def main():
    global exchange
    await redis_client.connect()

    logging.info(f"connected to reddis client")
    # Connect to RabbitMQ
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=5)

    # Bind to queue
    exchange = channel.default_exchange
    queue = await channel.declare_queue(RESPONSE_QUEUE, durable=True)
    await queue.consume(on_response_request)

    logging.info("📡 Response worker is running...")
    await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
