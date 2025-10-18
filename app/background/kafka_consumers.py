import asyncio
import sys
sys.path.append("../../")
from app.message_broker import KafkaConsumer

consumer_task = None
consumer_instance = None

async def kafka_plot_listener():
    """Listen to Kafka plot notifications and broadcast to WebSocket clients"""
    global consumer_instance
    consumer_instance = KafkaConsumer()

    async def handle_message(message: dict):
        await manager.broadcast(message)

    await consumer_instance.consume(handle_message)

async def start_consumers():
    """Start all Kafka consumers as background tasks"""
    global consumer_task
    consumer_task = asyncio.create_task(kafka_plot_listener())

async def stop_consumers():
    """Stop all Kafka consumers gracefully"""
    global consumer_task, consumer_instance
    if consumer_task:
        consumer_task.cancel()
    if consumer_instance:
        consumer_instance.close()
