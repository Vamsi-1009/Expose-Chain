"""
Utility functions for input detection and validation
"""
import validators
from typing import Literal


def detect_target_type(target: str) -> Literal["domain"]:
    """
    Detect the target type (domain only)

    Args:
        target: The target string to analyze

    Returns:
        "domain"
    """
    return "domain"


def is_valid_target(target: str) -> bool:
    """
    Check if a target is a valid domain name

    Args:
        target: The target string to validate

    Returns:
        True if valid domain, False otherwise
    """
    target = target.strip().lower()
    return validators.domain(target) is True
