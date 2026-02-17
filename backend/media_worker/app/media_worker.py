# Copyright 2026 by ReefConnect Team
"""Module defining the MediaWorker class."""

from reef_connect.common.blob_storage_client import BlobStorageClient
from reef_connect.common.database_client import DatabaseClient
from reef_connect.common.logger import get_logger
from reef_connect.common.media_codec import MediaCodec
from reef_connect.media_worker.app.media_processor import MediaProcessor

logger = get_logger(__name__)


class MediaWorker:
    """Core class for processing media asynchronously."""

    def __init__(self) -> None:
        """Initialize the MediaWorker."""
        self.blob_client = BlobStorageClient()
        self.db_client = DatabaseClient()
        self.media_processor = MediaProcessor()
        self.media_codec = MediaCodec()

    def process_media(self, media_id: str) -> None:
        """
        Process uploaded media.

        Args:
            media_id: The ID of the media to process.
        """
        try:
            logger.info(f"Starting processing for media_id: {media_id}")

            # Fetch media metadata from DB
            media_info = self.db_client.get_media(media_id)
            if not media_info:
                logger.error(f"No media info found for media_id: {media_id}")
                return

            blob_key = media_info.get("blob_key")
            if not blob_key:
                logger.error(f"No blob_key for media_id: {media_id}")
                return

            # Download and decode media
            raw_data = self.blob_client.download_raw(blob_key)
            decoded_media = self.media_codec.decode(raw_data, format="image")

            # Process media (generate thumbnails, etc.)
            processed_data = self.media_processor.generate_thumbnails(decoded_media)

            # Update DB with processed metadata
            self.db_client.update_media_status(media_id, "processed")
            self.db_client.insert_media_metadata(media_id, processed_data)

            # Publish MediaProcessed event (via container controller or direct)
            # For now, assume we have access to publisher
            logger.info(f"Successfully processed media_id: {media_id}")

        except Exception as e:
            logger.error(f"Error processing media_id {media_id}: {e}")
            # Publish ProcessingFailed event
            self.db_client.update_media_status(media_id, "failed")