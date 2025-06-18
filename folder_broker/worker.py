

import pika
import json
from database_client import DatabaseClient
from model_client import ModelClient
from predictor import WineQualityPredictor
from dotenv import load_dotenv
import os
import logging

load_dotenv(dotenv_path="../.env")
LOGGING_ENABLED = os.getenv("LOGGING", "0") == "1"
logging.basicConfig(level=logging.INFO if LOGGING_ENABLED else logging.CRITICAL)

print(os.getenv("OP_MODE"))


def on_request(ch, method, props, body):
    logging.info("Received request: %s", body)

    payload = json.loads(body)
    wine_id = payload.get("wine_id")
    measurement = payload.get("real_time_measurement")

    try:
        db = DatabaseClient()
        model = ModelClient()
        predictor = WineQualityPredictor(db, model)
        logging.info("Calling predictor...")
        # prediction = predictor.predict_quality(wine_id, measurement)
        raw_result = predictor.predict_quality(wine_id, measurement)

        # Parse prediction here
        if not isinstance(raw_result, dict) or "predictions" not in raw_result:
            response = {"error": "Invalid model response format"}
        elif not isinstance(raw_result["predictions"], list) or not raw_result["predictions"]:
            response = {"error": "Model returned empty predictions"}
        else:
            response = raw_result
        logging.info("Prediction result: %s", response)

        # response = {"prediction": prediction}
    except Exception as e:
        logging.exception("Error during prediction")

        response = {"error": str(e)}
    logging.info(json.dumps(response)+ "log1")
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    logging.info(json.dumps(response)+ "log2")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.URLParameters(        
        "amqp://guest:guest@rabbitmq:5672/"
        if os.getenv("OP_MODE") == "DOCKER"
        else "amqp://guest:guest@localhost:5672/"))
    channel = connection.channel()
    channel.queue_declare(queue='predict_queue')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='predict_queue', on_message_callback=on_request)

    print(" [x] Awaiting RPC prediction requests")
    channel.start_consuming()

if __name__ == "__main__":
    main()
