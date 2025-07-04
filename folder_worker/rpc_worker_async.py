import asyncio
import aio_pika
import json
import os
import logging
from dotenv import load_dotenv
from shared.database_client import DatabaseClient
from shared.model_client import ModelClient
from shared.predictor import WineQualityPredictor
from shared.send_log_good import EventHubLogger


load_dotenv(dotenv_path="../.env")


LOGGING_ENABLED = os.getenv("LOGGING", "0") == "1"
logging.basicConfig(level=logging.INFO if LOGGING_ENABLED else logging.CRITICAL)
if LOGGING_ENABLED:
    eventhub_logger = EventHubLogger()
    
    
AMQP_URL = (
    "amqp://guest:guest@rabbitmq:5672/"
    if os.getenv("OP_MODE") == "DOCKER"
    else "amqp://guest:guest@localhost:5672/"
)

REQUEST_QUEUE = "predict_request"

# ADD this global variable
exchange = None



async def on_request(message: aio_pika.IncomingMessage):
    global exchange
    async with message.process():
        payload = json.loads(message.body.decode())
        logging.info("Received request: %s", payload)

        wine_id = payload.get("wine_id")
        measurement = payload.get("real_time_measurement")

        try:
            db = DatabaseClient()
            model = ModelClient()
            predictor = WineQualityPredictor(db, model)
            raw_result = predictor.predict_quality(wine_id, measurement)

            if not isinstance(raw_result, dict) or "predictions" not in raw_result:
                response = {"error": "Invalid model response format"}
            elif not isinstance(raw_result["predictions"], list) or not raw_result["predictions"]:
                response = {"error": "Model returned empty predictions"}
            else:
                response = {
                    "wine_id": wine_id,
                    "predictions": raw_result["predictions"]
                }

        except Exception as e:
            logging.exception("Error during prediction")
            response = {"error": str(e)}

        logging.info("Sending response: %s", response)

        reply_message = aio_pika.Message(
            body=json.dumps(response).encode(),
            correlation_id=message.correlation_id
        )
        if LOGGING_ENABLED:
            log_message = {
                'app': 'alexandre-app',
                'data': {'Received request': payload,
                        "Sending response": response}
            }
            await eventhub_logger.log(message=log_message)
        # FIXED: Use global `exchange` instead of `message.channel.default_exchange`
        await exchange.publish(reply_message, routing_key=message.reply_to)


async def main():
    global exchange
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=3)

    # Declare exchange and store it
    # exchange = await channel.get_exchange("")  # default direct exchange
    exchange = channel.default_exchange  # this just references the built-in default

    queue = await channel.declare_queue(REQUEST_QUEUE, durable=True)
    await queue.consume(on_request)

    print(" [x] Async worker ready and waiting for prediction requests")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
