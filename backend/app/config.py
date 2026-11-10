"""Configuration loader for ExamAnt Backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", os.getenv("LOCAL_MONGO_URI", "mongodb://localhost:27018"))
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "examant_db")
AUTO_SEED_DEMO: bool = os.getenv("AUTO_SEED_DEMO", "true").lower() in ("true", "1", "yes")
