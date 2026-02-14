"""
Utility functions for input detection and validation
"""
import socket
import ipaddress
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


def is_private_ip(hostname: str) -> bool:
    """
    Check if hostname resolves to any private/internal IP address.
    Protects against SSRF (Server-Side Request Forgery) attacks.

    Args:
        hostname: Hostname or domain to check

    Returns:
        True if hostname resolves to a private/internal IP
    """
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
        for info in addr_infos:
            ip_str = info[4][0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return True
    except socket.gaierror:
        pass
    return False


def validate_target_not_internal(target: str) -> None:
    """
    Raise ValueError if target resolves to an internal/private IP.
    SSRF protection - prevents scanning internal networks.

    Args:
        target: Domain name to validate

    Raises:
        ValueError: If target resolves to a private IP
    """
    if is_private_ip(target):
        raise ValueError(
            "Target resolves to an internal/private IP address. "
            "Scanning internal networks is not allowed."
        )
