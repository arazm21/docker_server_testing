import asyncio
import aio_pika
import uuid
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv(dotenv_path="../.env")

LOGGING_ENABLED = os.getenv("LOGGING", "0") == "1"
logging.basicConfig(level=logging.INFO if LOGGING_ENABLED else logging.CRITICAL)

AMQP_URL = (
    "amqp://guest:guest@rabbitmq:5672/"
    if os.getenv("OP_MODE") == "DOCKER"
    else "amqp://guest:guest@localhost:5672/"
)

REQUEST_QUEUE = "predict_request"
RESPONSE_QUEUE = "predict_response"


class AsyncRpcClient:
    def __init__(self):
        self.futures = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(AMQP_URL)
        self.channel = await self.connection.channel()

        # Declare response and request queue and start listening
        await self.channel.declare_queue(REQUEST_QUEUE, durable=True)
        self.response_queue = await self.channel.declare_queue(RESPONSE_QUEUE, durable=True)
        await self.response_queue.consume(self.on_response)
        if LOGGING_ENABLED:
            logging.info(f"Connected to RabbitMQ at {AMQP_URL}")
            logging.info(f"Listening for responses on: {RESPONSE_QUEUE}")


    # async def on_response(self, message: aio_pika.IncomingMessage):
    #     async with message.process(ignore_processed=True):
    #         props = message.correlation_id
    #         if props in self.futures:
    #             payload = json.loads(message.body.decode())
    #             self.futures[props].set_result(payload)

    async def on_response(self, message: aio_pika.IncomingMessage):
        async with message.process():
            correlation_id = message.correlation_id
            if correlation_id in self.futures:
                response = json.loads(message.body.decode())
                if LOGGING_ENABLED:
                    logging.info(f"Received response for ID {correlation_id}: {response}")
                self.futures[correlation_id].set_result(response)
            else:
                if LOGGING_ENABLED:
                    logging.warning(f"Unknown correlation_id received: {correlation_id}")

    async def call(self, payload: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                correlation_id=correlation_id,
                reply_to=RESPONSE_QUEUE
            ),
            routing_key=REQUEST_QUEUE
        )
        if LOGGING_ENABLED:
            logging.info(f"Sent request {correlation_id}: {payload}")

        try:
            # response = await asyncio.wait_for(future, timeout=20)
            # return response
            response = await asyncio.wait_for(future, timeout=10)
            return {
                "request_id": correlation_id,
                **response
            }
        
        except asyncio.TimeoutError:
            logging.warning("Timed out waiting for worker response")
            return {
                "error": "timeout",
                "request_id": correlation_id
            }
        finally:
            # del self.futures[correlation_id]
            self.futures.pop(correlation_id, None)
