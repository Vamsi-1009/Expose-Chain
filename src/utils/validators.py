"""
Utility functions for input detection and validation
"""
import socket
import ipaddress
import logging
import validators
from typing import Literal

logger = logging.getLogger("exposechain")


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


def is_unsafe_ip(ip_str: str) -> bool:
    """
    Check if a single IP address is private/internal.
    Protects against SSRF (Server-Side Request Forgery) attacks.

    Args:
        ip_str: IP address literal to check

    Returns:
        True if the IP is private/loopback/reserved/link-local/multicast
    """
    ip = ipaddress.ip_address(ip_str)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_reserved
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
    )


def resolve_and_validate(hostname: str) -> list:
    """
    Resolve a hostname and validate that NONE of its IPs are internal.
    Returns the resolved IPs so callers can connect directly to a
    known-safe IP instead of re-resolving later (prevents DNS-rebinding
    TOCTOU: an attacker's DNS could return a public IP at validation
    time and a private IP at connection time).

    Args:
        hostname: Domain name to resolve

    Returns:
        List of resolved IP address strings

    Raises:
        ValueError: If the hostname fails to resolve or resolves to
            any internal/private IP address
    """
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: '{hostname}'")

    ips = []
    for info in addr_infos:
        ip_str = info[4][0]
        if is_unsafe_ip(ip_str):
            raise ValueError(
                "Target resolves to an internal/private IP address. "
                "Scanning internal networks is not allowed."
            )
        if ip_str not in ips:
            ips.append(ip_str)
    return ips


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
            if is_unsafe_ip(info[4][0]):
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
        logger.warning("Blocked SSRF attempt: target=%s resolves to an internal IP", target)
        raise ValueError(
            "Target resolves to an internal/private IP address. "
            "Scanning internal networks is not allowed."
        )
