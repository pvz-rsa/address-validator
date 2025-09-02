from pydantic import BaseModel, Field
from typing import List, Optional


class AddressComponents(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    cap: Optional[str] = Field(None, pattern=r"^\d{5}$")
    comune: Optional[str] = None
    provincia: Optional[str] = Field(None, pattern=r"^[A-Z]{2}$")
    country: Optional[str] = "Italia"


class NormalizeRequest(BaseModel):
    address: str


class NormalizeResponse(BaseModel):
    formatted: str
    components: AddressComponents
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str] = []


class ValidateRequest(BaseModel):
    components: AddressComponents


class ValidateResponse(BaseModel):
    valid: bool
    issues: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)


class SeedDataRequest(BaseModel):
    token: str


class HealthResponse(BaseModel):
    status: str