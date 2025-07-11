import asyncio
import json
import logging
import os
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aio_pika import connect_robust, Message
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


# Load env
load_dotenv(dotenv_path=".env")

# Config
AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
REQUEST_QUEUE = os.getenv("REQUEST_QUEUE", "predict_request")
RESPONSE_QUEUE = os.getenv("RESPONSE_QUEUE", "predict_response")
REDIS_PREFIX = "task:"
 
# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wine_api")

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- your HTML origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# RabbitMQ connection cache
channel_cache = None

callback_queue = None
futures_map = {}


class PredictionRequest(BaseModel):
    wine_id: int
    real_time_measurement: float


@app.on_event("startup")
async def startup_event():
    global channel_cache, callback_queue
    connection = await connect_robust(AMQP_URL)
    channel_cache = await connection.channel()
    await channel_cache.declare_queue(REQUEST_QUEUE, durable=True)
    await channel_cache.declare_queue(RESPONSE_QUEUE, durable=True)

    # Shared callback queue
    callback_queue = await channel_cache.declare_queue(
        name="predict_callback",
        durable=False,
        exclusive=False,
        auto_delete=True
    )

    # Response handler
    async def on_response(message):
        future = futures_map.pop(message.correlation_id, None)
        if future:
            body = json.loads(message.body.decode())
            future.set_result(body)
        else:
            logger.warning(f"⚠️ Unknown correlation_id: {message.correlation_id}")

    await callback_queue.consume(on_response, no_ack=True)

    logger.info("🔌 Connected to RabbitMQ and initialized shared callback queue")

@app.post("/send")
async def send_prediction(req: PredictionRequest):
    task_id = str(uuid.uuid4())

    payload = {
        "task_id": task_id,
        "wine_id": req.wine_id,
        "real_time_measurement": req.real_time_measurement,
    }
    
    # Send to queue
    await channel_cache.default_exchange.publish(
        Message(body=json.dumps(payload).encode()),
        routing_key=REQUEST_QUEUE
    )
    logger.info(f"📤 Sent task {task_id} to queue `{REQUEST_QUEUE}`")

    return {"task_id": task_id}

@app.get("/receive/{task_id}")
async def get_prediction(task_id: str):
    correlation_id = str(uuid.uuid4())
    future = asyncio.get_event_loop().create_future()
    futures_map[correlation_id] = future

    # Send request to RESPONSE_QUEUE
    payload = {"task_id": task_id}
    message = Message(
        body=json.dumps(payload).encode(),
        reply_to=callback_queue.name,
        correlation_id=correlation_id
    )
    await channel_cache.default_exchange.publish(
        message,
        routing_key=RESPONSE_QUEUE
    )

    try:
        result = await asyncio.wait_for(future, timeout=5)
        return result
    except asyncio.TimeoutError:
        futures_map.pop(correlation_id, None)
        raise HTTPException(status_code=504, detail="Response timeout")
