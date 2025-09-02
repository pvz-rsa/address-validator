from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import normalize, validate, datasets, health
from app.config import settings
import os

# Create FastAPI app instance
app = FastAPI(
    title="Italian Address Normalization Service",
    description="A microservice that normalizes messy Italian addresses into postal-correct, standardized format",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(normalize.router)
app.include_router(validate.router)
app.include_router(datasets.router)
app.include_router(health.router)

# Auto-seed database on startup for development
@app.on_event("startup")
async def startup_event():
    """Auto-seed database with Italian address data on startup."""
    try:
        import asyncio
        from app.repositories.caps_repo import CapsRepo
        from app.repositories.comuni_repo import ComuniRepo
        from app.repositories.synonyms_repo import SynonymsRepo
        import json
        
        # Wait a moment for MongoDB to be ready
        await asyncio.sleep(2)
        
        caps_repo = CapsRepo()
        comuni_repo = ComuniRepo()
        synonyms_repo = SynonymsRepo()
        
        # Check if data already exists
        if caps_repo.count() > 0:
            print("📊 Database already seeded")
            return
        
        print("🌱 Auto-seeding database with Italian address data...")
        
        # Seed CAPs data
        data_dir = os.path.join(os.path.dirname(__file__), "..", "comprehensive_italian_caps.json")
        if os.path.exists(data_dir):
            with open(data_dir, "r", encoding="utf-8") as f:
                caps_data = json.load(f)
            caps_repo.insert_many(caps_data)
        
        # Seed comuni data
        comuni_file = os.path.join(os.path.dirname(__file__), "data", "comprehensive_comuni.json")
        if os.path.exists(comuni_file):
            with open(comuni_file, "r", encoding="utf-8") as f:
                comuni_data = json.load(f)
            comuni_repo.insert_many(comuni_data)
        
        # Seed synonyms data
        synonyms_file = os.path.join(os.path.dirname(__file__), "data", "comprehensive_synonyms.json")
        if os.path.exists(synonyms_file):
            with open(synonyms_file, "r", encoding="utf-8") as f:
                synonyms_data = json.load(f)
            synonyms_repo.insert_many(synonyms_data)
        
        print(f"✅ Auto-seeded: {caps_repo.count()} CAPs, {comuni_repo.count()} comuni, {synonyms_repo.count()} synonyms")
        
    except Exception as e:
        print(f"⚠️ Auto-seeding failed: {e}")
        # Continue startup even if seeding fails


@app.get("/", tags=["root"])
async def root():
    """Serve the web UI for testing the service."""
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    else:
        return {
            "service": "Italian Address Normalization Service",
            "version": "1.0.0",
            "description": "Normalizes messy Italian addresses into postal-correct, standardized format",
            "endpoints": {
                "normalize": "/normalize - Normalize free-form addresses",
                "validate": "/validate - Validate structured address components", 
                "datasets": "/datasets - Manage datasets",
                "health": "/health - Health check",
                "docs": "/docs - API documentation"
            }
        }


@app.get("/api", tags=["root"])
async def api_info():
    """API endpoint information."""
    return {
        "service": "Italian Address Normalization Service",
        "version": "1.0.0",
        "description": "Normalizes messy Italian addresses into postal-correct, standardized format",
        "endpoints": {
            "normalize": "/normalize - Normalize free-form addresses",
            "validate": "/validate - Validate structured address components", 
            "datasets": "/datasets - Manage datasets",
            "health": "/health - Health check",
            "docs": "/docs - API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=10000,
        reload=settings.environment == "development"
    )