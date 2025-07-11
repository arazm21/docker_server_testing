import json
import asyncio
import os
from azure.eventhub import EventData,TransportType
from azure.eventhub.aio import EventHubProducerClient
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# print("cwd:", Path.cwd())
env_path = find_dotenv()
# print(".env located at:", env_path)
load_dotenv(env_path)

CONNECTION_STR = os.getenv("CONNECTION_STRING")

async def run():
    
    producer = EventHubProducerClient.from_connection_string(
                CONNECTION_STR,
                transport_type=TransportType.AmqpOverWebsocket,
                logging_enable=False
            )

    message = {
        'app': 'alexandre-app',
        'data': "თქვენი აპლიკაციის ლოგი"
    }
    json_message = json.dumps(message, ensure_ascii=False)
    event_data = EventData(json_message.encode('utf-8'))

    print("Sending message to Event Hub...")

    async with producer:
        event_data_batch = await producer.create_batch()
        event_data_batch.add(event_data)
        await producer.send_batch(event_data_batch)

    print("Message sent successfully.")

if __name__ == "__main__":
    asyncio.run(run())
