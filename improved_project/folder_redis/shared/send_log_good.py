import json
import asyncio
import os
from azure.eventhub import EventData, TransportType
from azure.eventhub.aio import EventHubProducerClient
from dotenv import load_dotenv, find_dotenv
import logging

# Load .env file

load_dotenv(find_dotenv())


CONNECTION_STR = os.getenv("CONNECTION_STRING")

logging.basicConfig(level=logging.INFO)
logging.info(f'connection string: {CONNECTION_STR}')

class EventHubLogger:
    def __init__(self, connection_str: str = CONNECTION_STR):
        self.connection_str = connection_str
        self.producer = EventHubProducerClient.from_connection_string(
            connection_str,
            transport_type=TransportType.AmqpOverWebsocket,
            logging_enable=False
        )

    async def log(self, message: dict):
        """
        Sends a log message to the Event Hub.
        """
        json_message = json.dumps(message, ensure_ascii=False)
        event_data = EventData(json_message.encode('utf-8'))

        async with self.producer:
            event_data_batch = await self.producer.create_batch()
            event_data_batch.add(event_data)
            await self.producer.send_batch(event_data_batch)
            logging.info("Message sent:", json_message)



