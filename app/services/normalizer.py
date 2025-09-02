import re
from typing import Optional, List, Tuple
from rapidfuzz import process, fuzz

from app.utils.text import normalize_text, extract_cap, extract_civic_number, clean_name, remove_country_suffixes
from app.utils.street_types import normalize_street_types, extract_street_info, get_full_street_name
from app.repositories.caps_repo import CapsRepo
from app.repositories.synonyms_repo import SynonymsRepo
from app.schemas.address import AddressComponents


class AddressNormalizer:
    def __init__(self, caps_repo: CapsRepo, synonyms_repo: SynonymsRepo):
        self.caps_repo = caps_repo
        self.synonyms_repo = synonyms_repo

    def normalize_city_name(self, city: str) -> str:
        """Translate city name from English/other languages to Italian."""
        if not city:
            return city
        
        # Get translation from synonyms repo
        return self.synonyms_repo.get_translation("city", city.strip())

    def extract_components(self, address_text: str) -> Tuple[AddressComponents, List[str]]:
        """
        Extract and normalize address components from free-form text.
        Returns tuple of (AddressComponents, issues_list).
        """
        issues = []
        
        # Initial text cleanup
        text = normalize_text(address_text)
        text = remove_country_suffixes(text)
        
        # Extract CAP first as it's most reliable
        cap = extract_cap(text)
        
        # Normalize street types (English to Italian)
        text = normalize_street_types(text)
        
        # Extract street information
        street_name, street_type = extract_street_info(text)
        full_street = get_full_street_name(street_name, street_type) if street_name and street_type else None
        
        # Extract civic number
        civic_number = extract_civic_number(text)
        
        # Extract potential city name (after comma, before CAP)
        city_candidates = self._extract_city_candidates(text, cap)
        
        # Resolve location data using CAP as source of truth
        comune, provincia, resolved_cap = self._resolve_location(cap, city_candidates, issues)
        
        # Use resolved CAP if we found one
        if resolved_cap and not cap:
            cap = resolved_cap
        
        components = AddressComponents(
            street=full_street,
            number=civic_number,
            cap=cap,
            comune=comune,
            provincia=provincia,
            country="Italia"
        )
        
        return components, issues

    def _extract_city_candidates(self, text: str, cap: Optional[str]) -> List[str]:
        """Extract potential city names from text."""
        candidates = []
        
        # Remove CAP and street info to isolate city names
        working_text = text
        if cap:
            working_text = working_text.replace(cap, "")
        
        # Remove street patterns
        street_pattern = r"\b(Via|Viale|Piazza|Piazzale|Corso|Località|Largo|Strada)\s+[^,]*"
        working_text = re.sub(street_pattern, "", working_text, flags=re.IGNORECASE)
        
        # Split by commas and extract potential city names
        parts = [part.strip() for part in working_text.split(",")]
        
        for part in parts:
            # Clean names (remove titles, extra punctuation)
            cleaned = clean_name(part)
            if cleaned and len(cleaned) > 2:  # Ignore very short strings
                # Translate city name
                translated = self.normalize_city_name(cleaned)
                if translated:
                    candidates.append(translated)
        
        return candidates

    def _resolve_location(self, cap: Optional[str], city_candidates: List[str], issues: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Resolve comune and provincia using CAP as source of truth.
        """
        comune = None
        provincia = None
        
        if cap:
            # CAP is present - use as source of truth
            cap_data = self.caps_repo.find_by_cap(cap)
            if cap_data:
                comune = cap_data["comune"]
                provincia = cap_data["provincia"]
                
                # Check if user-provided city conflicts with CAP
                if city_candidates:
                    cap_city_lower = comune.lower()
                    if not any(candidate.lower() == cap_city_lower for candidate in city_candidates):
                        issues.append("CITY_PROVINCE_OVERRIDDEN_BY_CAP")
            else:
                issues.append("CAP_UNKNOWN")
                # Try to use city candidates if CAP lookup failed
                if city_candidates:
                    comune = city_candidates[0]  # Use first candidate
        else:
            # No CAP - try to infer from city candidates
            if city_candidates:
                city = city_candidates[0]
                possible_caps = self.caps_repo.find_by_comune(city)
                
                if len(possible_caps) == 1:
                    # Unique CAP found
                    cap_data = possible_caps[0]
                    cap = cap_data["cap"]
                    comune = cap_data["comune"]
                    provincia = cap_data["provincia"]
                elif len(possible_caps) > 1:
                    # Multiple CAPs for this comune
                    issues.append("MULTIPLE_CAPS_FOR_COMUNE")
                    # Use the first one but indicate uncertainty
                    cap_data = possible_caps[0]
                    cap = cap_data["cap"]
                    comune = cap_data["comune"]
                    provincia = cap_data["provincia"]
                else:
                    # No CAP found for this comune
                    comune = city
                    issues.append("COMUNE_NOT_FOUND")
            else:
                issues.append("INSUFFICIENT_LOCALITY")
        
        return comune, provincia, cap

    def format_address(self, components: AddressComponents) -> str:
        """
        Format address components into standard Italian postal format:
        <Street + Number>, <CAP> <Comune> <Provincia>, Italia
        """
        parts = []
        
        # Street and number part
        street_part = []
        if components.street:
            street_part.append(components.street)
        if components.number:
            street_part.append(components.number)
        
        if street_part:
            parts.append(" ".join(street_part))
        
        # Location part
        location_parts = []
        if components.cap:
            location_parts.append(components.cap)
        if components.comune:
            location_parts.append(components.comune)
        if components.provincia:
            location_parts.append(components.provincia)
        
        if location_parts:
            parts.append(" ".join(location_parts))
        
        # Country
        parts.append("Italia")
        
        # Join with commas, clean up extra spaces/commas
        result = ", ".join(part for part in parts if part)
        result = re.sub(r"\s+", " ", result)
        result = re.sub(r",\s*,", ",", result)
        
        return result.strip()

    def calculate_confidence(self, issues: List[str]) -> float:
        """Calculate confidence score based on issues encountered."""
        confidence = 1.0
        
        # Define penalties for different types of issues
        penalty_map = {
            "CAP_UNKNOWN": 0.2,
            "CITY_PROVINCE_OVERRIDDEN_BY_CAP": 0.05,
            "MULTIPLE_CAPS_FOR_COMUNE": 0.15,
            "COMUNE_NOT_FOUND": 0.25,
            "INSUFFICIENT_LOCALITY": 0.3
        }
        
        for issue in issues:
            penalty = penalty_map.get(issue, 0.05)  # Default small penalty
            confidence -= penalty
        
        return max(0.0, min(1.0, confidence))