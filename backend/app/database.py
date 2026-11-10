"""
MongoDB Database Access Layer for ExamAnt.
Stores and retrieves `ExamInstanceDocument` records from the `exam_instances` collection.
Strictly relies on the running MongoDB instance (no static mock JSON fallback).
"""

import logging
from typing import List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.config import AUTO_SEED_DEMO, MONGO_DB_NAME, MONGO_URI
from app.schemas.models import ExamInstanceDocument, ExamInstanceSummary

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None


def get_collection() -> Optional[Collection]:
    """
    Return the `exam_instances` MongoDB collection, or None if unreachable.
    Logs clear instructions if MongoDB is offline.
    """
    global _mongo_client
    try:
        if _mongo_client is None:
            _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # Ping server to verify active connection
        _mongo_client.admin.command("ping")
        db = _mongo_client[MONGO_DB_NAME]
        collection = db["exam_instances"]
        collection.create_index("instance_id", unique=True)
        return collection
    except PyMongoError as exc:
        logger.error(
            "MongoDB is not reachable at %s (%s). "
            "Please ensure MongoDB container is started via 'docker compose up -d mongodb'.",
            MONGO_URI,
            exc,
        )
        return None


def ensure_initial_seed() -> int:
    """
    If `AUTO_SEED_DEMO` is enabled and MongoDB `exam_instances` collection is empty,
    automatically seeds programmatic datasets by invoking `seed_all_instances()`.
    """
    if not AUTO_SEED_DEMO:
        return 0

    collection = get_collection()
    if collection is None:
        logger.warning(
            "Cannot auto-seed: MongoDB is unavailable. "
            "Start the container with 'docker compose up -d mongodb' and run 'python -m scripts.seed_db'."
        )
        return 0

    if collection.count_documents({}) == 0:
        logger.info("Database is empty. Triggering programmatic seed into MongoDB...")
        from scripts.seed_db import seed_all_instances

        count = seed_all_instances()
        logger.info("Auto-seeded %d dataset instance(s) into MongoDB.", count)
        return count

    return 0


def list_all_instances() -> List[ExamInstanceSummary]:
    """Return summary metadata for all available dataset instances in MongoDB."""
    collection = get_collection()
    if collection is None:
        return []

    cursor = collection.find({}, {"_id": 0}).sort("instance_id", 1)
    docs = [ExamInstanceDocument(**doc) for doc in cursor]

    summaries: List[ExamInstanceSummary] = []
    for d in docs:
        days = len({s.day_index for s in d.slots})
        summaries.append(
            ExamInstanceSummary(
                instance_id=d.instance_id,
                name=d.name,
                seed=d.seed,
                description=d.description,
                num_courses=len(d.courses),
                num_students=len(d.students),
                num_enrollments=len(d.enrollments),
                num_slots=len(d.slots),
                num_days=days,
            )
        )
    return summaries


def get_instance_by_id(instance_id: str) -> Optional[ExamInstanceDocument]:
    """Fetch a single `ExamInstanceDocument` from MongoDB by `instance_id`."""
    collection = get_collection()
    if collection is None:
        return None

    raw = collection.find_one({"instance_id": instance_id}, {"_id": 0})
    if raw:
        return ExamInstanceDocument(**raw)
    return None


def upsert_instance(instance: ExamInstanceDocument) -> bool:
    """Insert or update an `ExamInstanceDocument` in MongoDB."""
    collection = get_collection()
    if collection is None:
        return False

    collection.update_one(
        {"instance_id": instance.instance_id},
        {"$set": instance.model_dump()},
        upsert=True,
    )
    return True
