"""
Utility functions for input detection and validation
"""
import ipaddress
import validators
from typing import Literal


def detect_target_type(target: str) -> Literal["domain", "ipv4", "ipv6"]:
    """
    Detect whether the input is a domain, IPv4, or IPv6 address
    
    Args:
        target: The target string to analyze
        
    Returns:
        "domain", "ipv4", or "ipv6"
    """
    target = target.strip().lower()
    
    # Try to parse as IP address
    try:
        ip = ipaddress.ip_address(target)
        if isinstance(ip, ipaddress.IPv4Address):
            return "ipv4"
        elif isinstance(ip, ipaddress.IPv6Address):
            return "ipv6"
    except ValueError:
        pass
    
    # If not an IP, assume it's a domain (already validated by pydantic)
    return "domain"


def is_valid_target(target: str) -> bool:
    """
    Check if a target is valid (domain or IP)
    
    Args:
        target: The target string to validate
        
    Returns:
        True if valid, False otherwise
    """
    target = target.strip().lower()
    
    # Check if it's a valid IP address
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    
    # Check if it's a valid domain
    return validators.domain(target) is True
