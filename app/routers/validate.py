from fastapi import APIRouter, Depends

from app.schemas.address import ValidateRequest, ValidateResponse
from app.services.validators import AddressValidator
from app.repositories.caps_repo import CapsRepo


router = APIRouter(prefix="/validate", tags=["validate"])


def get_caps_repo() -> CapsRepo:
    return CapsRepo()


def get_validator(caps_repo: CapsRepo = Depends(get_caps_repo)) -> AddressValidator:
    return AddressValidator(caps_repo)


@router.post("", response_model=ValidateResponse)
async def validate_address(
    payload: ValidateRequest,
    validator: AddressValidator = Depends(get_validator)
):
    """
    Validate structured address components.
    
    Takes address components and returns:
    - valid: Whether the address is valid
    - issues: List of validation problems found
    - confidence: Quality score (0-1)
    """
    is_valid, issues, confidence = validator.validate_components(payload.components)
    
    return ValidateResponse(
        valid=is_valid,
        issues=issues,
        confidence=confidence
    )