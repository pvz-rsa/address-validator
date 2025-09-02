import re
from typing import Dict, Tuple, Optional


def normalize_text(text: str) -> str:
    """Clean and normalize text by removing extra whitespace and trimming."""
    return re.sub(r"\s+", " ", text).strip()


def extract_cap(text: str) -> Optional[str]:
    """Extract 5-digit CAP (postal code) from text."""
    cap_pattern = re.compile(r"\b\d{5}\b")
    match = cap_pattern.search(text)
    return match.group(0) if match else None


def extract_civic_number(text: str) -> Optional[str]:
    """Extract civic number (digits optionally followed by letters) from text."""
    number_pattern = re.compile(r"\b\d+[A-Z]?\b", re.IGNORECASE)
    match = number_pattern.search(text)
    return match.group(0) if match else None


def clean_name(name: str) -> str:
    """Clean and normalize a name by removing extra punctuation and whitespace."""
    if not name:
        return ""
    
    # Remove common prefixes like titles
    cleaned = re.sub(r"^(Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+", "", name, flags=re.IGNORECASE)
    
    # Remove extra punctuation and normalize spaces
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = normalize_text(cleaned)
    
    return cleaned


def remove_country_suffixes(text: str) -> str:
    """Remove country suffixes from address text."""
    country_patterns = [
        r",?\s*Italy\s*$",
        r",?\s*Italia\s*$",
        r",?\s*IT\s*$"
    ]
    
    for pattern in country_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    return normalize_text(text)