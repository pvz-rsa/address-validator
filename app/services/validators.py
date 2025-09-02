from typing import List, Tuple
from app.schemas.address import AddressComponents
from app.repositories.caps_repo import CapsRepo


class AddressValidator:
    def __init__(self, caps_repo: CapsRepo):
        self.caps_repo = caps_repo

    def validate_components(self, components: AddressComponents) -> Tuple[bool, List[str], float]:
        """
        Validate address components and return validation status, issues, and confidence.
        Returns tuple of (is_valid, issues, confidence).
        """
        issues = []
        confidence = 1.0

        # Validate CAP format (already handled by Pydantic, but double-check)
        if components.cap and not self._is_valid_cap_format(components.cap):
            issues.append("INVALID_CAP_FORMAT")
            confidence -= 0.3

        # Validate provincia format (already handled by Pydantic, but double-check)
        if components.provincia and not self._is_valid_provincia_format(components.provincia):
            issues.append("INVALID_PROVINCIA_FORMAT")
            confidence -= 0.2

        # Cross-validate CAP with comune and provincia
        if components.cap:
            cap_data = self.caps_repo.find_by_cap(components.cap)
            if cap_data:
                # Check if provided comune matches CAP
                if components.comune and cap_data["comune"].lower() != components.comune.lower():
                    issues.append("COMUNE_CAP_MISMATCH")
                    confidence -= 0.4

                # Check if provided provincia matches CAP
                if components.provincia and cap_data["provincia"] != components.provincia:
                    issues.append("PROVINCIA_CAP_MISMATCH")
                    confidence -= 0.3
            else:
                issues.append("CAP_NOT_FOUND")
                confidence -= 0.5

        # Validate street format
        if components.street:
            if not self._is_valid_street_format(components.street):
                issues.append("INVALID_STREET_FORMAT")
                confidence -= 0.1

        # Validate civic number format
        if components.number:
            if not self._is_valid_number_format(components.number):
                issues.append("INVALID_NUMBER_FORMAT")
                confidence -= 0.1

        # Check completeness
        if not components.cap and not components.comune:
            issues.append("MISSING_LOCATION_INFO")
            confidence -= 0.5

        is_valid = len(issues) == 0
        confidence = max(0.0, min(1.0, confidence))

        return is_valid, issues, confidence

    def _is_valid_cap_format(self, cap: str) -> bool:
        """Check if CAP has valid 5-digit format."""
        return cap.isdigit() and len(cap) == 5

    def _is_valid_provincia_format(self, provincia: str) -> bool:
        """Check if provincia has valid 2-letter format."""
        return provincia.isalpha() and len(provincia) == 2 and provincia.isupper()

    def _is_valid_street_format(self, street: str) -> bool:
        """Basic validation of street format."""
        if not street or len(street.strip()) < 2:
            return False
        
        # Check if it contains reasonable characters
        import re
        # Allow letters, spaces, apostrophes, periods, and some common punctuation
        valid_pattern = r"^[A-Za-z\s\.'àáâäèéêëìíîïòóôöùúûü-]+$"
        return bool(re.match(valid_pattern, street))

    def _is_valid_number_format(self, number: str) -> bool:
        """Basic validation of civic number format."""
        if not number:
            return False
        
        import re
        # Should be digits optionally followed by letters (e.g., "123", "45A", "7bis")
        valid_pattern = r"^\d+[A-Za-z]*$"
        return bool(re.match(valid_pattern, number))