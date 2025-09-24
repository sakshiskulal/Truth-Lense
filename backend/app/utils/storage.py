import os
import logging
from typing import Tuple, Optional

try:
    import cloudinary
    import cloudinary.uploader
except Exception:  # pragma: no cover - optional dependency
    cloudinary = None

logger = logging.getLogger(__name__)


def _ensure_cloudinary_configured() -> bool:
    """Configure Cloudinary from environment if available.

    Accepts either CLOUDINARY_URL or individual CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET.
    Returns True if configured, False otherwise.
    """
    if cloudinary is None:
        logger.warning("Cloudinary SDK not installed. Install 'cloudinary' to enable uploads.")
        return False

    url = os.getenv("CLOUDINARY_URL")
    if url:
        try:
            cloudinary.config(cloudinary_url=url)
            return True
        except Exception as e:
            logger.error("Failed to configure Cloudinary from CLOUDINARY_URL: %s", e)
            return False

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if cloud_name and api_key and api_secret:
        try:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
            return True
        except Exception as e:
            logger.error("Failed to configure Cloudinary via discrete vars: %s", e)
            return False
    return False


def upload_to_cloudinary(file_path: str, resource_type: str = "auto") -> Tuple[bool, Optional[str], Optional[str]]:
    """Upload a local file to Cloudinary.

    Returns (ok, secure_url, public_id).
    """
    if not _ensure_cloudinary_configured():
        return False, None, None

    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            folder=os.getenv("CLOUDINARY_FOLDER", "truthlens/uploads"),
        )
        return True, result.get("secure_url"), result.get("public_id")
    except Exception as e:
        logger.error("Cloudinary upload failed: %s", e)
        return False, None, None
