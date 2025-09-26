from google.cloud import pubsub_v1
import json


class PubSubMessagePublisher:
    """
    Class for publishing messages to Google Cloud Pub/Sub topics.

    Attributes:
        project_id (str): The Google Cloud project ID associated with the Pub/Sub topic.
    """

    def __init__(self, project_id):
        """
        Initializes the PubSubMessagePublisher with the project ID.

        Args:
            project_id (str): The Google Cloud project ID.
        """
        self.project_id = project_id

    def send_message(self, topic_name: str, message: dict):
        """
        Publishes a message to a specific Pub/Sub topic.

        Args:
            topic_name (str): The name of the Pub/Sub topic to publish to.
            message (dict): The message data to be published.

        Raises:
            Exception: If an error occurs during message publishing.
        """

        try:
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(self.project_id, topic_name)
            message_json = json.dumps(message)

            future = publisher.publish(topic_path, data=message_json.encode('utf-8'))
            future.result()  # Block until the message is published
            logger.debug(
                event="Topic publishing",
                message=f"Message published to topic: {topic_name}",
                username=message["username"]
            )
        except Exception as e:
            logger.error(
                event="Topic publishing failure",
                message=f"Failed to publish message to topic: {topic_name}",
                username=message["username"],
                error=str(e)
            )
            raise
