from typing import Dict, Any, List
from pymongo import MongoClient
from datetime import datetime
import os


class LogsRepo:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
        self.db = self.client[os.getenv("MONGO_DB", "addresses")]
        self.col = self.db["normalizations"]
        self.col.create_index("timestamp")

    async def save(self, log_data: Dict[str, Any]) -> bool:
        try:
            log_entry = {
                "input": log_data.get("input"),
                "output": log_data.get("output"),
                "timestamp": log_data.get("ts", datetime.utcnow().isoformat()),
                "user_agent": log_data.get("user_agent"),
                "latency_ms": log_data.get("latency_ms")
            }
            self.col.insert_one(log_entry)
            return True
        except Exception as e:
            print(f"Error saving log: {e}")
            return False

    def find_recent(self, limit: int = 100) -> List[dict]:
        return list(self.col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))

    def count(self) -> int:
        return self.col.count_documents({})

    def clear(self) -> bool:
        try:
            self.col.delete_many({})
            return True
        except Exception:
            return False