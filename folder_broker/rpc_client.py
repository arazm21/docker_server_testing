import uuid
import pika
import json
import threading
import time  # NEW IMPORT
from dotenv import load_dotenv
import os
import logging
load_dotenv(dotenv_path="../.env")
 
LOGGING_ENABLED = os.getenv("LOGGING", "0") == "1"
logging.basicConfig(level=logging.INFO if LOGGING_ENABLED else logging.CRITICAL)

class RpcClient:
    def __init__(self, amqp_url=            
            "amqp://guest:guest@rabbitmq:5672/"
            if os.getenv("OP_MODE") == "DOCKER"
            else "amqp://guest:guest@localhost:5672/"):
        self.connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        self.response = None
        self.corr_id = None
        self.lock = threading.Event()

    def on_response(self, ch, method, props, body):
        logging.info("on_response triggered")
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)
            logging.info(f"Received response: {self.response}")
            self.lock.set()

    def call(self, payload: dict):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.lock.clear()

        self.channel.basic_publish(
            exchange='',
            routing_key='predict_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(payload)
        )
        logging.info(f"Sent request: {json.dumps(payload)}")

        # Process events while waiting for response
        timeout = 10
        start_time = time.time()
        while not self.lock.is_set():
            # Check if we've timed out
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                logging.warning("Timed out waiting for worker response")
                return None
                
            # Process network events (NEW CRITICAL PART)
            self.connection.process_data_events(time_limit=timeout - elapsed)
            
            # Small sleep to prevent busy-waiting
            time.sleep(0.05)

        logging.info(f"Got response from worker: {self.response}")
        return self.response