import aio_pika
import json
import os

class RabbitMQClient:
    def __init__(self):
        self.url = os.getenv("AMQP_URL")
        self.request_queue = os.getenv("REQUEST_QUEUE", "predict_request")
        self.status_queue = os.getenv("STATUS_QUEUE", "status_request")
        self.conn = None
        self.channel = None

    async def connect(self):
        self.conn = await aio_pika.connect_robust(self.url)
        self.channel = await self.conn.channel()
        await self.channel.declare_queue(self.request_queue, durable=True)
        await self.channel.declare_queue(self.status_queue, durable=True)

    async def send_task(self, payload):
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(payload).encode()),
            routing_key=self.request_queue
        )

    async def send_status_check(self, payload):
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(payload).encode()),
            routing_key=self.status_queue
        )
