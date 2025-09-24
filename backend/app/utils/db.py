import os
import logging
from functools import lru_cache

from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()  # search in current/parent directories

# Also try backend/.env if present (relative to this file)
_backend_root_env = Path(__file__).resolve().parents[2] / ".env"
if _backend_root_env.exists():
    load_dotenv(dotenv_path=_backend_root_env, override=False)


logger = logging.getLogger(__name__)


def _redact_uri(uri: str) -> str:
    """Redact credentials from a MongoDB URI for safe logging."""
    try:
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(uri)
        netloc = parsed.netloc
        if "@" in netloc:
            # Split credentials and host
            creds, host = netloc.split("@", 1)
            if ":" in creds:
                user, _ = creds.split(":", 1)
                redacted_creds = f"{user}:***"
            else:
                redacted_creds = "***"
            netloc = f"{redacted_creds}@{host}"
        redacted = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        return redacted
    except Exception:
        return uri


@lru_cache(maxsize=1)
def _get_client() -> MongoClient:
    """Create and cache a MongoDB client.

    Reads MONGODB_URI from env/.env; does not assume a DB in the URI.
    """
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    # Keep a short server selection timeout so endpoints fail fast if DB is down
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    return client


def _extract_db_name_from_uri(uri: str) -> str | None:
    """Try to extract the DB name from a MongoDB URI path.

    Returns None if not present.
    """
    try:
        from urllib.parse import urlparse

        path = urlparse(uri).path or ""
        # path looks like "/dbname" when present
        if path and path != "/":
            return path.lstrip("/").split("/")[0].split("?")[0]
    except Exception:
        pass
    return None


def get_db():
    client = _get_client()
    # Prefer explicit DB name from env if provided
    db_name = os.getenv("MONGODB_DB_NAME")
    if not db_name:
        # If URI includes a default DB, use it; otherwise fallback
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = _extract_db_name_from_uri(uri)
        if not db_name:
            # Try pymongo's helper in case URI driver options define it
            try:
                db = client.get_default_database()
                if db is not None:
                    try:
                        logger.info(
                            "MongoDB using default database from client; uri=%s",
                            _redact_uri(uri),
                        )
                    except Exception:
                        pass
                    return db
            except ConfigurationError:
                pass
            # Final fallback default
            db_name = os.getenv("MONGODB_DEFAULT_DB", "truthlens")
    else:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    # Log the resolved values (redacted URI)
    try:
        logger.info("MongoDB connecting; uri=%s db=%s", _redact_uri(uri), db_name)
    except Exception:
        pass

    return client[db_name]


def get_users_collection():
    return get_db()["users"]
