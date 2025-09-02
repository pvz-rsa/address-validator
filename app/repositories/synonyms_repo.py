from typing import Optional, List, Dict
from pymongo import MongoClient
import os


class SynonymsRepo:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
        self.db = self.client[os.getenv("MONGO_DB", "addresses")]
        self.col = self.db["synonyms"]
        self.col.create_index("type")
        self.col.create_index("original")

    def find_by_type_and_original(self, synonym_type: str, original: str) -> Optional[dict]:
        return self.col.find_one({"type": synonym_type, "original": original.lower()}, {"_id": 0})

    def find_all_by_type(self, synonym_type: str) -> List[dict]:
        return list(self.col.find({"type": synonym_type}, {"_id": 0}))

    def get_translation(self, synonym_type: str, original: str) -> str:
        result = self.find_by_type_and_original(synonym_type, original.lower())
        return result["translation"] if result else original

    def insert_many(self, synonyms_data: List[dict]) -> bool:
        try:
            processed_data = []
            for item in synonyms_data:
                processed_data.append({
                    "type": item["type"],
                    "original": item["original"].lower(),
                    "translation": item["translation"]
                })
            self.col.insert_many(processed_data)
            return True
        except Exception as e:
            print(f"Error inserting synonyms data: {e}")
            return False

    def count(self) -> int:
        return self.col.count_documents({})

    def clear(self) -> bool:
        try:
            self.col.delete_many({})
            return True
        except Exception:
            return False