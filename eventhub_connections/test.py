import os
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from dotenv import load_dotenv, find_dotenv


from pathlib import Path
print("cwd:", Path.cwd())
print(".env found at:", find_dotenv())

load_dotenv(dotenv_path="../.env")

# Extract your environment variables
ENDPOINT = os.getenv("ENDPOINT")  # Example: sb://evhns-weu-d-ml.servicebus.windows.net/
SHAREDACCESSKEYNAME = os.getenv("SHAREDACCESSKEYNAME")  # Example: RootManageSharedAccessKey
SHAREDACCESSKEY = os.getenv("SHAREDACCESSKEY")  # Example: Your primary key
ENTITYPATH = os.getenv("ENTITYPATH")  # Event Hub name

WORKER_REPLICAS=os.getenv("WORKER_REPLICAS")
print(ENDPOINT)
print(WORKER_REPLICAS)
CONNECTION_STRING=os.getenv("CONNECTION_STRING")
print(CONNECTION_STRING)


print("cwd:", Path.cwd())
env_path = find_dotenv()
print(".env located at:", env_path)
load_dotenv(env_path)

for key in ["ENDPOINT", "SHAREDACCESSKEYNAME", "SHAREDACCESSKEY", "ENTITYPATH","CONNECTION_STRING", "EVENT_HUB_NAME"]:
    
    print(f"{key} → {os.getenv(key)}")