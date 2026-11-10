"""
MongoDB Database Access Layer for ExamAnt.
Stores and retrieves `ExamInstanceDocument` records from the `exam_instances` collection.
Includes a graceful fallback to `scripts/sample_instances.json` if MongoDB is temporarily offline.
"""

import json
import logging
from typing import List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.config import AUTO_SEED_DEMO, MONGO_DB_NAME, MONGO_URI, SAMPLE_DATA_PATH
from app.schemas.models import ExamInstanceDocument, ExamInstanceSummary

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None


def get_collection() -> Optional[Collection]:
    """Return the `exam_instances` MongoDB collection, or None if unreachable."""
    global _mongo_client
    try:
        if _mongo_client is None:
            _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # Ping server to verify connection
        _mongo_client.admin.command("ping")
        db = _mongo_client[MONGO_DB_NAME]
        collection = db["exam_instances"]
        collection.create_index("instance_id", unique=True)
        return collection
    except PyMongoError as exc:
        logger.warning("MongoDB connection unavailable (%s). Using JSON fallback.", exc)
        return None


def load_sample_instances_from_json() -> List[ExamInstanceDocument]:
    """Load fallback/starter instances from `scripts/sample_instances.json`."""
    if not SAMPLE_DATA_PATH.exists():
        return []
    with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
        raw_list = json.load(f)
    return [ExamInstanceDocument(**item) for item in raw_list]


def ensure_initial_seed() -> int:
    """
    If `AUTO_SEED_DEMO` is enabled and `exam_instances` collection is empty,
    automatically seed the starter instances from `scripts/sample_instances.json`.
    """
    if not AUTO_SEED_DEMO:
        return 0
    collection = get_collection()
    if collection is None:
        return 0
    if collection.count_documents({}) == 0:
        samples = load_sample_instances_from_json()
        for inst in samples:
            collection.update_one(
                {"instance_id": inst.instance_id},
                {"$set": inst.model_dump()},
                upsert=True,
            )
        logger.info("Auto-seeded %d starter instance(s) into MongoDB.", len(samples))
        return len(samples)
    return 0


def list_all_instances() -> List[ExamInstanceSummary]:
    """Return summary metadata for all available dataset instances."""
    collection = get_collection()
    docs: List[ExamInstanceDocument] = []

    if collection is not None:
        cursor = collection.find({}, {"_id": 0}).sort("instance_id", 1)
        docs = [ExamInstanceDocument(**doc) for doc in cursor]
    else:
        docs = load_sample_instances_from_json()

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
    """Fetch a single `ExamInstanceDocument` by `instance_id`."""
    collection = get_collection()
    if collection is not None:
        raw = collection.find_one({"instance_id": instance_id}, {"_id": 0})
        if raw:
            return ExamInstanceDocument(**raw)

    # Fallback to local JSON if not found or DB offline
    for inst in load_sample_instances_from_json():
        if inst.instance_id == instance_id:
            return inst
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
