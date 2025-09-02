from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "addresses"
    admin_token: str = "changeme"
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()