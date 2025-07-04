import json
from azure.eventhub import EventData
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="../.env")

Endpoint=os.getenv("ENDPOINT")
SharedAccessKeyName=os.getenv("SHAREDACCESSKEYNAME")
SharedAccessKey=os.getenv("SHAREDACCESSKEY")
EntityPath=os.getenv("ENTITYPATH")

message = {'app': 'aleksandre-app', 'data': "{თქვენი აპლიკაციის ლოგი}"}
json_message = json.dumps(message, ensure_ascii=False)  # ensure_ascii=False keeps Georgian characters


event_data = EventData(json_message.encode('utf-8'))




# import asyncio

# from azure.eventhub import EventData
# from azure.eventhub.aio import EventHubProducerClient

# EVENT_HUB_CONNECTION_STR = Endpoint
# EVENT_HUB_NAME = EntityPath

# async def run():
#     # Create a producer client to send messages to the event hub.
#     # Specify a connection string to your event hubs namespace and
#     # the event hub name.
#     producer = EventHubProducerClient.from_connection_string(
#         conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME
#     )
#     async with producer:
#         # Create a batch.
#         event_data_batch = await producer.create_batch()

#         # Add events to the batch.
#         event_data_batch.add(event_data)

#         # Send the batch of events to the event hub.
#         await producer.send_batch(event_data_batch)

# asyncio.run(run())

import asyncio

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential

EVENT_HUB_FULLY_QUALIFIED_NAMESPACE = "sb://evhns-weu-d-ml"
EVENT_HUB_NAME = "testhub"

credential = DefaultAzureCredential()

async def run():
    # Create a producer client to send messages to the event hub.
    # Specify a credential that has correct role assigned to access
    # event hubs namespace and the event hub name.
    producer = EventHubProducerClient(
        fully_qualified_namespace=EVENT_HUB_FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        credential=credential,
    )
    print("Producer client created successfully.") 
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()

        # Add events to the batch.
        event_data_batch.add(event_data)

        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)

        # Close credential when no longer needed.
        await credential.close()

asyncio.run(run())