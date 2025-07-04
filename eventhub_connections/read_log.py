import json
import asyncio
import os
from azure.eventhub import TransportType
from azure.eventhub.aio import EventHubConsumerClient
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# print("cwd:", Path.cwd())
env_path = find_dotenv()
# print(".env located at:", env_path)
load_dotenv(env_path)

CONNECTION_STR = os.getenv("CONNECTION_STRING")
# print("connection string :" + CONNECTION_STR)

async def on_event(partition_context, event):
    """
    Callback function to process each event received from the Event Hub
    """
    try:
        # Decode the event data
        event_data = event.body_as_str(encoding='utf-8')
        
        # Parse JSON if applicable
        try:
            parsed_data = json.loads(event_data)
            print(f"Received structured message: {parsed_data}")
        except json.JSONDecodeError:
            print(f"Received raw message: {event_data}")
        
        # Print additional event metadata
        print(f"  - Partition: {partition_context.partition_id}")
        print(f"  - Offset: {event.offset}")
        print(f"  - Sequence Number: {event.sequence_number}")
        print(f"  - Enqueued Time: {event.enqueued_time}")
        print("-" * 50)
        
        # Update checkpoint to mark this event as processed
        await partition_context.update_checkpoint(event)
        
    except Exception as e:
        print(f"Error processing event: {e}")

async def run():
    # Create consumer client
    consumer = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",  # Use default consumer group
        transport_type=TransportType.AmqpOverWebsocket,
        logging_enable=False
    )
    
    print("Starting Event Hub consumer...")
    print("Listening for messages... (Press Ctrl+C to stop)")
    
    try:
        async with consumer:
            # Receive events from all partitions
            await consumer.receive(
                on_event=on_event,
                starting_position="-1"  # Start from the latest events
            )
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    except Exception as e:
        print(f"Error in consumer: {e}")

if __name__ == "__main__":
    asyncio.run(run())