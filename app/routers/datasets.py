from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
import json
import os

from app.schemas.address import SeedDataRequest
from app.schemas.responses import SuccessResponse
from app.repositories.caps_repo import CapsRepo
from app.repositories.comuni_repo import ComuniRepo
from app.repositories.synonyms_repo import SynonymsRepo


router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_caps_repo() -> CapsRepo:
    return CapsRepo()


def get_comuni_repo() -> ComuniRepo:
    return ComuniRepo()


def get_synonyms_repo() -> SynonymsRepo:
    return SynonymsRepo()


def verify_admin_token(x_admin_token: Optional[str] = Header(None)):
    """Verify admin token for protected endpoints."""
    expected_token = os.getenv("ADMIN_TOKEN", "changeme")
    if not x_admin_token or x_admin_token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@router.post("/seed", response_model=SuccessResponse)
async def seed_datasets(
    caps_repo: CapsRepo = Depends(get_caps_repo),
    comuni_repo: ComuniRepo = Depends(get_comuni_repo),
    synonyms_repo: SynonymsRepo = Depends(get_synonyms_repo),
    _: None = Depends(verify_admin_token)
):
    """
    Seed the database with initial datasets.
    Requires X-Admin-Token header with valid token.
    """
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
        # Load and insert CAPs data - use comprehensive dataset
        project_root = os.path.join(os.path.dirname(__file__), "..", "..")
        caps_file = os.path.join(project_root, "comprehensive_italian_caps.json")
        if os.path.exists(caps_file):
            with open(caps_file, "r", encoding="utf-8") as f:
                caps_data = json.load(f)
            caps_repo.clear()  # Clear existing data
            caps_repo.insert_many(caps_data)
        else:
            # Fallback to original small dataset
            fallback_caps_file = os.path.join(data_dir, "seed_caps.json")
            if os.path.exists(fallback_caps_file):
                with open(fallback_caps_file, "r", encoding="utf-8") as f:
                    caps_data = json.load(f)
                caps_repo.clear()  # Clear existing data
                caps_repo.insert_many(caps_data)
        
        # Load and insert comuni data - use comprehensive dataset
        comprehensive_comuni_file = os.path.join(data_dir, "comprehensive_comuni.json")
        if os.path.exists(comprehensive_comuni_file):
            with open(comprehensive_comuni_file, "r", encoding="utf-8") as f:
                comuni_data = json.load(f)
            comuni_repo.clear()  # Clear existing data
            comuni_repo.insert_many(comuni_data)
        else:
            # Fallback to original small dataset
            fallback_comuni_file = os.path.join(data_dir, "seed_comuni.json")
            if os.path.exists(fallback_comuni_file):
                with open(fallback_comuni_file, "r", encoding="utf-8") as f:
                    comuni_data = json.load(f)
                comuni_repo.clear()  # Clear existing data
                comuni_repo.insert_many(comuni_data)
        
        # Load and insert synonyms data - use comprehensive dataset
        comprehensive_synonyms_file = os.path.join(data_dir, "comprehensive_synonyms.json")
        if os.path.exists(comprehensive_synonyms_file):
            with open(comprehensive_synonyms_file, "r", encoding="utf-8") as f:
                synonyms_data = json.load(f)
            synonyms_repo.clear()  # Clear existing data
            synonyms_repo.insert_many(synonyms_data)
        else:
            # Fallback to original small dataset
            fallback_synonyms_file = os.path.join(data_dir, "seed_synonyms.json")
            if os.path.exists(fallback_synonyms_file):
                with open(fallback_synonyms_file, "r", encoding="utf-8") as f:
                    synonyms_data = json.load(f)
                synonyms_repo.clear()  # Clear existing data
                synonyms_repo.insert_many(synonyms_data)
        
        # Count loaded records
        caps_count = caps_repo.count()
        comuni_count = comuni_repo.count()
        synonyms_count = synonyms_repo.count()
        
        return SuccessResponse(
            success=True,
            message="Datasets seeded successfully",
            data={
                "caps_loaded": caps_count,
                "comuni_loaded": comuni_count,
                "synonyms_loaded": synonyms_count
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding datasets: {str(e)}")


@router.get("/stats", response_model=dict)
async def get_dataset_stats(
    caps_repo: CapsRepo = Depends(get_caps_repo),
    comuni_repo: ComuniRepo = Depends(get_comuni_repo),
    synonyms_repo: SynonymsRepo = Depends(get_synonyms_repo)
):
    """Get statistics about loaded datasets."""
    return {
        "caps_count": caps_repo.count(),
        "comuni_count": comuni_repo.count(),
        "synonyms_count": synonyms_repo.count()
    }