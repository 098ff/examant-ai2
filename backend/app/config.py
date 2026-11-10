"""Configuration loader for ExamAnt Backend."""

import os
import socket
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _resolve_mongo_uri() -> str:
    """
    Resolve MongoDB connection URI.
    If running outside a Docker container and MONGO_URI points to the container
    internal hostname 'mongodb' (which cannot be resolved by host DNS),
    automatically fall back to LOCAL_MONGO_URI (default: mongodb://localhost:27018).
    """
    uri = os.getenv("MONGO_URI")
    local_uri = os.getenv("LOCAL_MONGO_URI", "mongodb://localhost:27018")

    if not uri:
        return local_uri

    # Check if host 'mongodb' is unresolvable (e.g. running on host machine instead of Docker network)
    if "://mongodb:" in uri or uri.startswith("mongodb://mongodb"):
        if not os.path.exists("/.dockerenv"):
            try:
                socket.gethostbyname("mongodb")
            except (socket.gaierror, OSError):
                return local_uri

    return uri


MONGO_URI: str = _resolve_mongo_uri()
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "examant_db")
AUTO_SEED_DEMO: bool = os.getenv("AUTO_SEED_DEMO", "true").lower() in ("true", "1", "yes")
