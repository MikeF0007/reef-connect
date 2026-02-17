# Copyright 2026 by ReefConnect Team
"""Module defining the MediaWorkerContainerController class."""

import signal
import sys

from reef_connect.common.container.event_based_container_controller import EventBasedContainerController
from reef_connect.common.container.routing_definitions import ContainerRouting, KafkaRouting
from reef_connect.common.logger import get_logger
from reef_connect.media_worker.app.media_worker_event_service import MediaWorkerEventService

logger = get_logger(__name__)


class MediaWorkerContainerController(EventBasedContainerController):
    """Container controller for the MediaWorker service."""

    def __init__(self) -> None:
        """Initialize the MediaWorkerContainerController."""
        # Define config with container routing
        container_routing = ContainerRouting(
            container_name="media-worker-container",
            kafka_routings=[
                KafkaRouting(
                    server_address="localhost:9092",  # Placeholder
                    group_id="reef_consumer_media_worker",
                    receive_topics=["media-uploaded"],
                    callback=MediaWorkerEventService().run,
                )
            ],
        )
        config = {
            'container_routing': container_routing,
        }
        super().__init__(config)

    def shutdown(self) -> None:
        """Shutdown the container controller."""
        logger.info("Shutting down MediaWorkerContainerController")
        if hasattr(self, 'kafka_mngr'):
            self.kafka_mngr.shutdown()
        super().shutdown()


def handle_sigterm(signal_number, frame):
    """Handle SIGTERM signal."""
    logger.info("SIGTERM received, shutting down...")
    if 'server' in globals():
        server.shutdown()
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)


if __name__ == "__main__":
    server = MediaWorkerContainerController()
    server.start()