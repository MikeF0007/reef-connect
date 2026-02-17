# Copyright 2026 by ReefConnect Team
"""Module defining the MediaWorkerEventService class."""

from reef_connect.common.logger import get_logger
from reef_connect.media_worker.app.media_worker import MediaWorker

logger = get_logger(__name__)


class MediaWorkerEventService:
    """Service to handle Redpanda events for media processing."""

    def __init__(self) -> None:
        """Initialize the MediaWorkerEventService."""
        self.media_worker = MediaWorker()

    def run(self, messages: list, topic: str = None) -> None:
        """
        Process incoming Redpanda messages.

        Args:
            messages: List of messages received.
            topic: The topic from which messages were received.
        """
        try:
            logger.info(f"Received messages from topic: {topic}")

            if topic == "media-uploaded":
                logger.info("Processing media-uploaded events")
                for record in messages:
                    media_id = record.value.get("media_id")
                    user_id = record.value.get("user_id")
                    if media_id:
                        logger.info(f"Processing media_id: {media_id}")
                        self.media_worker.process_media(media_id)
                    else:
                        logger.error("Missing media_id in message")
        except Exception as e:
            logger.error(f"Error processing messages: {e}")