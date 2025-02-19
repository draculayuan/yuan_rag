from google.cloud import pubsub_v1
from typing import Callable, Dict, Any
import json
import os

class PubSubClient:
    def __init__(self, project_id: str, topic_name: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.project_id = project_id
        self.topic_path = self.publisher.topic_path(project_id, topic_name)

    def publish_message(self, message_data: Dict[str, Any]) -> str:
        """Publish a message to the Pub/Sub topic."""
        data = json.dumps(message_data).encode("utf-8")
        future = self.publisher.publish(self.topic_path, data)
        return future.result()

    def create_subscription(self, subscription_name: str) -> str:
        """Create a subscription if it doesn't exist."""
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_name
        )
        try:
            self.subscriber.create_subscription(
                request={"name": subscription_path, "topic": self.topic_path}
            )
        except Exception as e:
            if "already exists" not in str(e):
                raise
        return subscription_path

    def subscribe(self, subscription_name: str, callback: Callable) -> None:
        """Subscribe to messages with a callback function."""
        subscription_path = self.create_subscription(subscription_name)
        
        def callback_wrapper(message):
            try:
                data = json.loads(message.data.decode("utf-8"))
                callback(data)
                message.ack()
            except Exception as e:
                print(f"Error processing message: {e}")
                message.nack()

        streaming_pull_future = self.subscriber.subscribe(
            subscription_path, callback=callback_wrapper
        )
        return streaming_pull_future 
