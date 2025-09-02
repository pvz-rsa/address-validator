from fastapi import APIRouter, Depends, Request
from datetime import datetime
import time

from app.schemas.address import NormalizeRequest, NormalizeResponse
from app.services.normalizer import AddressNormalizer
from app.repositories.caps_repo import CapsRepo
from app.repositories.synonyms_repo import SynonymsRepo
from app.repositories.logs_repo import LogsRepo


router = APIRouter(prefix="/normalize", tags=["normalize"])


def get_caps_repo() -> CapsRepo:
    return CapsRepo()


def get_synonyms_repo() -> SynonymsRepo:
    return SynonymsRepo()


def get_logs_repo() -> LogsRepo:
    return LogsRepo()


def get_normalizer(
    caps_repo: CapsRepo = Depends(get_caps_repo),
    synonyms_repo: SynonymsRepo = Depends(get_synonyms_repo)
) -> AddressNormalizer:
    return AddressNormalizer(caps_repo, synonyms_repo)


@router.post("", response_model=NormalizeResponse)
async def normalize_address(
    payload: NormalizeRequest,
    request: Request,
    normalizer: AddressNormalizer = Depends(get_normalizer),
    logs_repo: LogsRepo = Depends(get_logs_repo)
):
    """
    Normalize a free-form Italian address into standardized postal format.
    
    Takes an address string and returns:
    - formatted: Standard postal format
    - components: Structured address parts  
    - confidence: Quality score (0-1)
    - issues: List of warnings/corrections made
    """
    start_time = time.time()
    
    # Extract and normalize components
    components, issues = normalizer.extract_components(payload.address)
    
    # Format the address
    formatted_address = normalizer.format_address(components)
    
    # Calculate confidence
    confidence = normalizer.calculate_confidence(issues)
    
    # Create response
    response = NormalizeResponse(
        formatted=formatted_address,
        components=components,
        confidence=confidence,
        issues=issues
    )
    
    # Log the operation
    latency_ms = int((time.time() - start_time) * 1000)
    user_agent = request.headers.get("user-agent", "")
    
    await logs_repo.save({
        "input": payload.address,
        "output": response.dict(),
        "ts": datetime.utcnow().isoformat(),
        "user_agent": user_agent,
        "latency_ms": latency_ms
    })
    
    return response