# Import models here to make them available when importing from the models module
from .person import Person  # Base model (not a table)
from .moba_player import (
    MobaPlayer,  # Inherits from Person
    ROLE_TOP,
    ROLE_JUNGLE,
    ROLE_MID,
    ROLE_ADC,
    ROLE_SUPPORT,
    VALID_ROLES,
    CONTRACT_STATUS_SIGNED,
    CONTRACT_STATUS_FREE_AGENT,
    CONTRACT_STATUS_TRANSFER_LISTED,
    CONTRACT_STATUS_RETIRED,
    VALID_CONTRACT_STATUSES,
)

__all__ = [
    "Person",
    "MobaPlayer",
    "ROLE_TOP",
    "ROLE_JUNGLE",
    "ROLE_MID",
    "ROLE_ADC",
    "ROLE_SUPPORT",
    "VALID_ROLES",
    "CONTRACT_STATUS_SIGNED",
    "CONTRACT_STATUS_FREE_AGENT",
    "CONTRACT_STATUS_TRANSFER_LISTED",
    "CONTRACT_STATUS_RETIRED",
    "VALID_CONTRACT_STATUSES",
]
