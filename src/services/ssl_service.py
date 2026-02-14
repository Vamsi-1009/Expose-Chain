"""
SSL Certificate Service for ExposeChain
Handles SSL/TLS certificate validation and analysis
"""
import ssl
import socket
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import OpenSSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cachetools import TTLCache

logger = logging.getLogger("exposechain")


class SSLService:
    """Service for SSL/TLS certificate analysis"""

    def __init__(self):
        self.timeout = 10
        self.default_port = 443
        self._cache = TTLCache(maxsize=128, ttl=300)  # 5 min TTL
    
    def get_certificate(self, hostname: str, port: int = None) -> Dict[str, Any]:
        """
        Retrieve SSL certificate from a hostname
        
        Args:
            hostname: Domain name to check
            port: Port number (default: 443)
            
    Returns:
            Dictionary with certificate data
        """
        if port is None:
            port = self.default_port

        cache_key = f"ssl:{hostname}:{port}"
        if cache_key in self._cache:
            logger.debug("Cache hit for %s", cache_key)
            return self._cache[cache_key]

        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate in DER format
                    der_cert = ssock.getpeercert(binary_form=True)
                    
                    # Get certificate info
                    cert_dict = ssock.getpeercert()
                    
                    # Get SSL/TLS version
                    ssl_version = ssock.version()
                    
                    # Get cipher suite
                    cipher = ssock.cipher()
                    
                    # Parse certificate with cryptography
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    
                    result = {
                        "success": True,
                        "hostname": hostname,
                        "port": port,
                        "certificate": self._parse_certificate(cert, cert_dict),
                        "ssl_version": ssl_version,
                        "cipher_suite": {
                            "name": cipher[0] if cipher else None,
                            "protocol": cipher[1] if cipher else None,
                            "bits": cipher[2] if cipher else None
                        }
                    }
                    self._cache[cache_key] = result
                    return result
                    
        except socket.timeout:
            return {
                "success": False,
                "hostname": hostname,
                "port": port,
                "error": f"Connection timeout after {self.timeout} seconds"
            }
        except ssl.SSLError as e:
            return {
                "success": False,
                "hostname": hostname,
                "port": port,
                "error": f"SSL Error: {str(e)}"
            }
        except socket.gaierror:
            return {
                "success": False,
                "hostname": hostname,
                "port": port,
                "error": "Could not resolve hostname"
            }
        except Exception as e:
            return {
                "success": False,
                "hostname": hostname,
                "port": port,
                "error": str(e)
            }
    
    def _parse_certificate(self, cert: x509.Certificate, cert_dict: dict) -> Dict[str, Any]:
        """
        Parse certificate details
        
        Args:
            cert: Certificate object
            cert_dict: Certificate dictionary from SSL
            
        Returns:
            Parsed certificate information
        """
        # Get subject information
        subject = {}
        for attr in cert.subject:
            subject[attr.oid._name] = attr.value
        
        # Get issuer information
        issuer = {}
        for attr in cert.issuer:
            issuer[attr.oid._name] = attr.value
        
        # Get SANs (Subject Alternative Names)
        sans = []
        try:
            san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            sans = [dns.value for dns in san_ext.value]
        except x509.ExtensionNotFound:
            pass
        
        # Get dates
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        
        # Get key info
        key_info = self._get_key_info(cert)
        
        return {
            "subject": subject,
            "issuer": issuer,
            "version": cert.version.name,
            "serial_number": str(cert.serial_number),
            "signature_algorithm": cert.signature_algorithm_oid._name,
            "public_key_algorithm": key_info["algorithm"],
            "key_size": key_info["key_size"],
            "key_type": key_info["key_type"],
            "valid_from": not_before.isoformat(),
            "valid_until": not_after.isoformat(),
            "days_until_expiration": (not_after - datetime.now(not_after.tzinfo)).days,
            "is_expired": datetime.now(not_after.tzinfo) > not_after,
            "subject_alternative_names": sans,
            "san_count": len(sans)
        }
    
    def _get_key_info(self, cert: x509.Certificate) -> Dict[str, Any]:
        """
        Get detailed public key information
        
        Args:
            cert: Certificate object
            
        Returns:
            Dictionary with key type, size, and algorithm
        """
        try:
            public_key = cert.public_key()
            key_class = public_key.__class__.__name__
            
            key_size = None
            key_type = "Unknown"
            
            if "RSA" in key_class:
                key_type = "RSA"
                if hasattr(public_key, 'key_size'):
                    key_size = public_key.key_size
            elif "EC" in key_class or "Elliptic" in key_class:
                key_type = "ECC"
                if hasattr(public_key, 'key_size'):
                    key_size = public_key.key_size
            elif "DSA" in key_class:
                key_type = "DSA"
                if hasattr(public_key, 'key_size'):
                    key_size = public_key.key_size
            
            return {
                "algorithm": key_class,
                "key_type": key_type,
                "key_size": key_size
            }
        except:
            return {
                "algorithm": "Unknown",
                "key_type": "Unknown",
                "key_size": None
            }
    
    def analyze_certificate_security(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze certificate security and provide insights
        
        Args:
            cert_data: Certificate data from get_certificate
            
        Returns:
            Security analysis results
        """
        if not cert_data.get("success"):
            return {
                "security_score": 0,
                "risk_level": "unknown",
                "issues": ["Certificate could not be retrieved"],
                "recommendations": []
            }
        
        cert = cert_data.get("certificate", {})
        issues = []
        recommendations = []
        score = 100
        
        # Check expiration
        days_left = cert.get("days_until_expiration", 0)
        if cert.get("is_expired"):
            issues.append("Certificate has EXPIRED")
            score -= 50
        elif days_left < 7:
            issues.append(f"Certificate expires in {days_left} days - URGENT renewal needed")
            score -= 30
        elif days_left < 30:
            issues.append(f"Certificate expires in {days_left} days - Renewal recommended")
            score -= 15
        
        # Check key size based on key type
        key_size = cert.get("key_size")
        key_type = cert.get("key_type", "Unknown")
        
        if key_size:
            if key_type == "RSA":
                if key_size < 2048:
                    issues.append(f"Weak RSA key: {key_size} bits (minimum 2048 recommended)")
                    score -= 25
                elif key_size < 3072:
                    # 2048 is acceptable but not ideal
                    pass
            elif key_type == "ECC":
                if key_size < 256:
                    issues.append(f"Weak ECC key: {key_size} bits (minimum 256 recommended)")
                    score -= 25
                # ECC 256-bit is equivalent to RSA 3072-bit, which is strong
        
        # Check signature algorithm
        sig_algo = cert.get("signature_algorithm", "")
        if "sha1" in sig_algo.lower():
            issues.append("Using deprecated SHA-1 signature algorithm")
            score -= 20
            recommendations.append("Upgrade to SHA-256 or better")
        
        # Check SSL/TLS version
        ssl_version = cert_data.get("ssl_version", "")
        if ssl_version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
            issues.append(f"Using outdated protocol: {ssl_version}")
            score -= 20
            recommendations.append("Upgrade to TLS 1.2 or TLS 1.3")
        elif ssl_version == "TLSv1.3":
            # Excellent - latest version
            pass
        
        # Check cipher suite
        cipher = cert_data.get("cipher_suite", {})
        cipher_name = cipher.get("name", "")
        if "RC4" in cipher_name or "DES" in cipher_name:
            issues.append(f"Weak cipher suite: {cipher_name}")
            score -= 15
        
        # Determine risk level
        if score >= 85:
            risk_level = "low"
        elif score >= 70:
            risk_level = "medium"
        elif score >= 50:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Add general recommendations
        if not recommendations:
            if score < 100:
                recommendations.append("Certificate configuration meets modern standards")
        
        # Build key strength description
        key_strength = "Unknown"
        if key_type == "RSA" and key_size:
            if key_size >= 3072:
                key_strength = "Strong (RSA 3072+ bit)"
            elif key_size >= 2048:
                key_strength = "Adequate (RSA 2048 bit)"
            else:
                key_strength = "Weak"
        elif key_type == "ECC" and key_size:
            if key_size >= 384:
                key_strength = "Very Strong (ECC 384+ bit)"
            elif key_size >= 256:
                key_strength = "Strong (ECC 256 bit ~ RSA 3072 bit)"
            else:
                key_strength = "Weak"
        
        return {
            "security_score": max(0, score),
            "risk_level": risk_level,
            "issues": issues if issues else ["No major issues detected"],
            "recommendations": recommendations if recommendations else ["Certificate configuration is secure"],
            "details": {
                "key_type": key_type,
                "key_strength": key_strength,
                "protocol_version": ssl_version,
                "expires_in_days": days_left,
                "is_valid": not cert.get("is_expired", True)
            }
        }
    
    def check_hostname_match(self, hostname: str, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if hostname matches certificate
        
        Args:
            hostname: Hostname to check
            cert_data: Certificate data
            
        Returns:
            Hostname validation results
        """
        if not cert_data.get("success"):
            return {
                "matches": False,
                "reason": "Certificate not available"
            }
        
        cert = cert_data.get("certificate", {})
        subject = cert.get("subject", {})
        common_name = subject.get("commonName", "")
        sans = cert.get("subject_alternative_names", [])
        
        # Check common name
        if hostname == common_name:
            return {
                "matches": True,
                "matched_via": "common_name",
                "matched_value": common_name
            }
        
        # Check wildcard common name
        if common_name.startswith("*."):
            wildcard_domain = common_name[2:]
            if hostname.endswith(wildcard_domain):
                return {
                    "matches": True,
                    "matched_via": "wildcard_common_name",
                    "matched_value": common_name
                }
        
        # Check SANs
        for san in sans:
            if hostname == san:
                return {
                    "matches": True,
                    "matched_via": "subject_alternative_name",
                    "matched_value": san
                }
            
            # Check wildcard SAN
            if san.startswith("*."):
                wildcard_domain = san[2:]
                if hostname.endswith(wildcard_domain):
                    return {
                        "matches": True,
                        "matched_via": "wildcard_san",
                        "matched_value": san
                    }
        
        return {
            "matches": False,
            "reason": f"Hostname '{hostname}' not found in certificate",
            "certificate_names": {
                "common_name": common_name,
                "sans": sans[:5]  # Show first 5 SANs only
            }
        }
