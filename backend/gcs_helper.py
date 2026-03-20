"""
gcs_helper.py
Helper functions for interacting with Google Cloud Storage.
"""

import os
import uuid
import logging
from typing import Optional
from google.cloud import storage

logger = logging.getLogger("CivicBridge.GCS")

def upload_image_to_gcs(image_bytes: bytes, mime_type: str) -> Optional[str]:
    """
    Uploads an image to Google Cloud Storage and returns the public URI.
    Requires GCS_BUCKET_NAME to be set in the environment.
    """
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        logger.warning("GCS_BUCKET_NAME not set. Skipping Cloud Storage upload.")
        return None

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        extension = mime_type.split("/")[-1] if "/" in mime_type else "jpg"
        filename = f"civic_complaints/{uuid.uuid4().hex[:12]}.{extension}"
        
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        
        url = f"gs://{bucket_name}/{filename}"
        logger.info(f"Successfully uploaded image to GCS: {url}")
        return url
        
    except Exception as e:
        logger.error(f"GCS Upload failed: {e}", exc_info=True)
        return None
