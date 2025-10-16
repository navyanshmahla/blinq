from pydantic import BaseModel, Field

class KafkaConfig(BaseModel):
    """Kafka connection configuration"""
    bootstrap_servers: list[str] = Field(default=["localhost:9092"])
    topic_plot_notifications: str = Field(default="plot_notifications")
    group_id: str = Field(default="plot_consumers")
    auto_offset_reset: str = Field(default="latest")
    enable_auto_commit: bool = Field(default=True)

kafka_config = KafkaConfig()
