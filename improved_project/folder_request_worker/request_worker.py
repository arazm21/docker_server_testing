import asyncio
import aio_pika
import json
import os
import logging
from dotenv import load_dotenv
from shared.redis_client import RedisClient  # Local helper for Redis
from shared.database_client import DatabaseClient
from shared.model_client import ModelClient
from shared.predictor import WineQualityPredictor
from shared.send_log_good import EventHubLogger

load_dotenv(dotenv_path="../.env")

# Logging config
LOGGING_ENABLED = os.getenv("LOGGING", "0") == "1"
logging.basicConfig(level=logging.INFO if LOGGING_ENABLED else logging.CRITICAL)
if LOGGING_ENABLED:
    eventhub_logger = EventHubLogger()

# RabbitMQ & Redis config
AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
REQUEST_QUEUE = os.getenv("REQUEST_QUEUE", "predict_request")

redis_client = RedisClient()

async def on_request(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            logging.info("Received request: %s", payload)

            task_id = payload["task_id"]
            wine_id = payload["wine_id"]
            measurement = payload["real_time_measurement"]

            # Immediately mark task as PENDING in Redis
            await redis_client.set_status(task_id, "PENDING")
            await asyncio.sleep(10)
            # Run prediction
            db = DatabaseClient()
            model = ModelClient()
            predictor = WineQualityPredictor(db, model)

            raw_result = predictor.predict_quality(wine_id, measurement)

            if not isinstance(raw_result, dict) or "predictions" not in raw_result:
                result = {"error": "Invalid model response format"}
            elif not raw_result["predictions"]:
                result = {"error": "Model returned empty predictions"}
            else:
                result = {"wine_id": wine_id, "predictions": raw_result["predictions"]}

            # Write final result to Redis
            await redis_client.set_status(task_id, "DONE", result)

            if LOGGING_ENABLED:
                log_message = {
                    'app': 'wine-request-worker',
                    'data': {
                        'Received request': payload,
                        'Computed result': result
                    }
                }
                await eventhub_logger.log(message=log_message)

        except Exception as e:
            logging.exception("Worker failed")
            await redis_client.set_status(task_id, "ERROR", {"error": str(e)})

async def main():
    await redis_client.connect()

    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=5)

    queue = await channel.declare_queue(REQUEST_QUEUE, durable=True)
    await queue.consume(on_request)

    print(" [x] Request worker started and waiting for messages")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
