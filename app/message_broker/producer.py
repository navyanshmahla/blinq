from kafka import KafkaProducer as KP
import json
from .config import kafka_config

class KafkaProducer:
    """Kafka message producer"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.producer = KP(
                bootstrap_servers=kafka_config.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        return cls._instance

    async def send_plot_notification(self, plot_data: dict):
        """Send plot completion notification"""
        self.producer.send(kafka_config.topic_plot_notifications, plot_data)
        self.producer.flush()

    def close(self):
        """Close producer connection"""
        self.producer.close()
