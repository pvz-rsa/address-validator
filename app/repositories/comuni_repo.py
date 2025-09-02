from typing import Optional, List
from pymongo import MongoClient
import os


class ComuniRepo:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
        self.db = self.client[os.getenv("MONGO_DB", "addresses")]
        self.col = self.db["comuni"]
        self.col.create_index("comune", unique=True)
        self.col.create_index("provincia")

    def find_by_comune(self, comune: str) -> Optional[dict]:
        return self.col.find_one({"comune": comune}, {"_id": 0})

    def find_by_provincia(self, provincia: str) -> List[dict]:
        return list(self.col.find({"provincia": provincia}, {"_id": 0}))

    def insert_many(self, comuni_data: List[dict]) -> bool:
        try:
            self.col.insert_many(comuni_data)
            return True
        except Exception as e:
            print(f"Error inserting comuni data: {e}")
            return False

    def count(self) -> int:
        return self.col.count_documents({})

    def clear(self) -> bool:
        try:
            self.col.delete_many({})
            return True
        except Exception:
            return False