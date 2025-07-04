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


async def read_all_messages_batch():
    consumer = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        transport_type=TransportType.AmqpOverWebsocket,
        logging_enable=False
    )
    all_messages = []
    print("Reading all messages from Event Hub using batch method...")

    async with consumer:
        partition_ids = await consumer.get_partition_ids()
        print(f"Found partitions: {partition_ids}")

        for partition_id in partition_ids:
            print(f"\nReading from partition {partition_id}...")
            props = await consumer.get_partition_properties(partition_id)
            if props['last_enqueued_sequence_number'] == -1:
                print(f"Partition {partition_id} is empty")
                continue

            async def on_event_batch(partition_context, event_batch):
                if not event_batch:
                    print("Empty batch, might be end of stream")
                    return
                for ev in event_batch:
                    data = ev.body_as_str(encoding='utf-8')
                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError:
                        payload = data
                    msg = {
                        'data': payload,
                        'partition_id': partition_context.partition_id,
                        'offset': ev.offset,
                        'sequence_number': ev.sequence_number,
                        'enqueued_time': ev.enqueued_time.isoformat() if ev.enqueued_time else None
                    }
                    all_messages.append(msg)
                    print("Received:", msg)

            await consumer.receive_batch(
                on_event_batch=on_event_batch,
                partition_id=partition_id,
                starting_position="@earliest",
                max_batch_size=100,
                max_wait_time=5,
                prefetch=100
            )

    print("Total messages:", len(all_messages))
    return all_messages




async def run():
    # Read all existing messages using the fixed receive method
    # messages = await read_all_messages()
    
    # Alternative: Use batch method if you prefer
    messages = await read_all_messages_batch()
    
    # Optionally save to file
    if messages:
        with open('eventhub_messages.json', 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print(f"Messages saved to eventhub_messages.json")
    
    return messages

if __name__ == "__main__":
    asyncio.run(run())
    
    
    
    
# async def read_all_messages():
#     """
#     Read all existing messages from the Event Hub
#     """
#     consumer = EventHubConsumerClient.from_connection_string(
#         CONNECTION_STR,
#         consumer_group="$Default",
#         transport_type=TransportType.AmqpOverWebsocket,
#         logging_enable=False
#     )
    
#     all_messages = []
#     message_count = 0
    
#     print("Reading all messages from Event Hub...")
    
#     try:
#         async with consumer:
#             # Get partition information
#             partition_ids = await consumer.get_partition_ids()
#             print(f"Found {len(partition_ids)} partitions: {partition_ids}")
            
#             # Read from each partition
#             for partition_id in partition_ids:
#                 print(f"\nReading from partition {partition_id}...")
                
#                 # Get partition properties to check if there are messages
#                 partition_props = await consumer.get_partition_properties(partition_id)
#                 print(f"Partition properties: {partition_props}")
#                 print(f"Partition {partition_id} - Last enqueued sequence: {partition_props['last_enqueued_sequence_number']}")
                
#                 if partition_props['last_enqueued_sequence_number'] == -1:
#                     print(f"No messages in partition {partition_id}")
#                     continue
                
#                 partition_message_count = 0
                
#                 # Use the correct method: receive
#                 try:
#                     print(f"Starting to receive events from partition {partition_id}...")
                    
#                     # Create a list to store events for this partition
#                     partition_events = []
                    
#                     # Set up event handler
#                     async def on_event(partition_context, event):
#                         nonlocal partition_message_count, message_count
                        
#                         try:
#                             # Decode the event data
#                             event_data = event.body_as_str(encoding='utf-8')
                            
#                             # Parse JSON if applicable
#                             try:
#                                 parsed_data = json.loads(event_data)
#                                 message_info = {
#                                     'data': parsed_data,
#                                     'partition_id': partition_context.partition_id,
#                                     'offset': event.offset,
#                                     'sequence_number': event.sequence_number,
#                                     'enqueued_time': event.enqueued_time.isoformat() if event.enqueued_time else None
#                                 }
#                             except json.JSONDecodeError:
#                                 message_info = {
#                                     'data': event_data,
#                                     'partition_id': partition_context.partition_id,
#                                     'offset': event.offset,
#                                     'sequence_number': event.sequence_number,
#                                     'enqueued_time': event.enqueued_time.isoformat() if event.enqueued_time else None
#                                 }
                            
#                             all_messages.append(message_info)
#                             partition_events.append(message_info)
#                             partition_message_count += 1
#                             message_count += 1
                            
#                             # Print message details
#                             print(f"Message {message_count}:")
#                             print(f"  Data: {message_info['data']}")
#                             print(f"  Partition: {partition_context.partition_id}")
#                             print(f"  Offset: {event.offset}")
#                             print(f"  Sequence: {event.sequence_number}")
#                             print(f"  Time: {event.enqueued_time}")
#                             print("-" * 50)
                            
#                         except Exception as e:
#                             print(f"Error processing event: {e}")
                    
#                     # Start receiving - this will run until we break out
#                     # Fixed: Removed max_batch_size parameter and used correct parameters
#                     receive_task = asyncio.create_task(
#                         consumer.receive(
#                             on_event=on_event,
#                             partition_id=partition_id,
#                             starting_position="@earliest",
#                             max_wait_time=5,  # This is a valid parameter for receive method
#                             prefetch=100     # This controls how many events to prefetch
#                         )
#                     )
                    
#                     # Wait for a reasonable time to get all messages
#                     try:
#                         await asyncio.wait_for(receive_task, timeout=30)
#                     except asyncio.TimeoutError:
#                         print(f"Timeout reached for partition {partition_id}")
#                         receive_task.cancel()
#                         try:
#                             await receive_task
#                         except asyncio.CancelledError:
#                             pass
                            
#                 except Exception as e:
#                     print(f"Error reading from partition {partition_id}: {e}")
                
#                 print(f"Found {partition_message_count} messages in partition {partition_id}")
    
#     except Exception as e:
#         print(f"Error reading messages: {e}")
    
#     print(f"\nTotal messages read: {message_count}")
#     return all_messages
