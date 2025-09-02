from typing import Optional, List
from pymongo import MongoClient
import os


class CapsRepo:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
        self.db = self.client[os.getenv("MONGO_DB", "addresses")]
        self.col = self.db["caps"]
        self.col.create_index("cap", unique=True)
        self.col.create_index("comune")

    def find_by_cap(self, cap: str) -> Optional[dict]:
        return self.col.find_one({"cap": cap}, {"_id": 0})

    def find_by_comune(self, comune: str) -> List[dict]:
        return list(self.col.find({"comune": comune}, {"_id": 0}))

    def insert_many(self, caps_data: List[dict]) -> bool:
        try:
            self.col.insert_many(caps_data)
            return True
        except Exception as e:
            print(f"Error inserting caps data: {e}")
            return False

    def count(self) -> int:
        return self.col.count_documents({})

    def clear(self) -> bool:
        try:
            self.col.delete_many({})
            return True
        except Exception:
            return False