import re
from typing import Dict


# Street type translations from English to Italian
STREET_TYPES_TRANSLATIONS = {
    "square": "Piazza",
    "sq": "Piazza",
    "plaza": "Piazza",
    "place": "Piazza",
    "street": "Via",
    "st": "Via",
    "road": "Via",
    "rd": "Via",
    "avenue": "Viale",
    "ave": "Viale",
    "av": "Viale",
    "boulevard": "Viale",
    "blvd": "Viale",
    "lane": "Via",
    "ln": "Via",
    "way": "Via",
    "drive": "Via",
    "dr": "Via",
    "court": "Corte",
    "ct": "Corte",
    "circle": "Piazza",
    "localita": "Località",
    "locality": "Località"
}

# Italian street type abbreviations to full forms
ITALIAN_ABBREVIATIONS = {
    "p.zza": "Piazza",
    "p.za": "Piazza",
    "p.le": "Piazzale",
    "v.le": "Viale",
    "str.": "Strada",
    "c.so": "Corso",
    "loc.": "Località",
    "l.go": "Largo"
}


def normalize_street_types(text: str) -> str:
    """Normalize street types from English to Italian and expand abbreviations."""
    result = text
    
    # First normalize English street types to Italian
    for english, italian in STREET_TYPES_TRANSLATIONS.items():
        # Use word boundaries to avoid partial matches
        pattern = rf"\b{re.escape(english)}\b"
        result = re.sub(pattern, italian, result, flags=re.IGNORECASE)
    
    # Then expand Italian abbreviations
    for abbrev, full in ITALIAN_ABBREVIATIONS.items():
        # Case insensitive replacement for abbreviations
        pattern = rf"\b{re.escape(abbrev)}\b"
        result = re.sub(pattern, full, result, flags=re.IGNORECASE)
    
    return result


def extract_street_info(text: str) -> tuple[str, str]:
    """
    Extract street name and type from text.
    Returns tuple of (street_name, street_type) or (None, None) if not found.
    """
    # Common Italian street types in order of specificity
    street_types = [
        "Piazzale", "Piazza", "Viale", "Via", "Corso", "Località", "Largo", "Strada", "Corte"
    ]
    
    for street_type in street_types:
        # Look for pattern: street_type + space + street_name
        pattern = rf"\b({street_type})\s+([^,\d]*?)(?=\s*\d|\s*,|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            street_name = match.group(2).strip()
            if street_name:  # Make sure we found a name
                return street_name, street_type
    
    return None, None


def get_full_street_name(street_name: str, street_type: str) -> str:
    """Combine street type and name into full street name."""
    if not street_name or not street_type:
        return ""
    
    return f"{street_type} {street_name}".strip()