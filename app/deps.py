from app.repositories.caps_repo import CapsRepo
from app.repositories.comuni_repo import ComuniRepo
from app.repositories.synonyms_repo import SynonymsRepo
from app.repositories.logs_repo import LogsRepo
from app.services.normalizer import AddressNormalizer
from app.services.validators import AddressValidator


def get_caps_repo() -> CapsRepo:
    """Dependency to get CapsRepo instance."""
    return CapsRepo()


def get_comuni_repo() -> ComuniRepo:
    """Dependency to get ComuniRepo instance."""
    return ComuniRepo()


def get_synonyms_repo() -> SynonymsRepo:
    """Dependency to get SynonymsRepo instance."""
    return SynonymsRepo()


def get_logs_repo() -> LogsRepo:
    """Dependency to get LogsRepo instance."""
    return LogsRepo()


def get_address_normalizer(
    caps_repo: CapsRepo = None,
    synonyms_repo: SynonymsRepo = None
) -> AddressNormalizer:
    """Dependency to get AddressNormalizer instance."""
    if caps_repo is None:
        caps_repo = get_caps_repo()
    if synonyms_repo is None:
        synonyms_repo = get_synonyms_repo()
    
    return AddressNormalizer(caps_repo, synonyms_repo)


def get_address_validator(caps_repo: CapsRepo = None) -> AddressValidator:
    """Dependency to get AddressValidator instance."""
    if caps_repo is None:
        caps_repo = get_caps_repo()
    
    return AddressValidator(caps_repo)