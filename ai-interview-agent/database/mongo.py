"""MongoDB access helpers with in-memory fallback for local development."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from config import MONGO_URI, DB_NAME, USE_FAKE_DB


class InMemoryCollection:
    """Small Mongo-like in-memory collection for local demos."""

    def __init__(self) -> None:
        self.data: Dict[str, Dict[str, Any]] = {}

    def insert_one(self, doc: Dict[str, Any]) -> Any:
        _id = doc.get("_id", str(uuid.uuid4()))
        doc["_id"] = _id
        doc.setdefault("created_at", datetime.utcnow().isoformat())
        self.data[_id] = doc

        class Result:
            inserted_id = _id

        return Result()

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self.data.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> None:
        target = self.find_one(query)
        if not target:
            return
        if "$set" in update:
            target.update(update["$set"])


class Database:
    """Wrapper over MongoDB client or in-memory fallback collections."""

    def __init__(self) -> None:
        self._use_fake = USE_FAKE_DB
        self.users = InMemoryCollection()
        self.resumes = InMemoryCollection()
        self.interviews = InMemoryCollection()
        self.answers = InMemoryCollection()
        self.reports = InMemoryCollection()

        if not self._use_fake:
            try:
                from pymongo import MongoClient

                client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                client.server_info()  # Force connectivity check.
                db = client[DB_NAME]
                self.users = db.users
                self.resumes = db.resumes
                self.interviews = db.interviews
                self.answers = db.answers
                self.reports = db.reports
            except Exception:
                # Fall back gracefully when MongoDB is unavailable.
                self._use_fake = True


db = Database()
