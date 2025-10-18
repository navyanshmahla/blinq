from kafka import KafkaConsumer as KC
import json
from .config import kafka_config
from typing import Callable, Awaitable

class KafkaConsumer:
    """Kafka message consumer"""
    def __init__(self):
        self.consumer = KC(
            kafka_config.topic_plot_notifications,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id=kafka_config.group_id,
            auto_offset_reset=kafka_config.auto_offset_reset,
            enable_auto_commit=kafka_config.enable_auto_commit,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    async def consume(self, callback: Callable[[dict], Awaitable[None]]):
        """Consume messages and invoke callback"""
        for message in self.consumer:
            await callback(message.value)

    def close(self):
        """Close consumer connection"""
        self.consumer.close()
