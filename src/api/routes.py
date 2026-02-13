"""
API Routes for ExposeChain
"""
from fastapi import APIRouter, HTTPException
from src.models import ScanRequest, ScanResponse
from src.utils import detect_target_type
from src.services import DNSService, WHOISService, GeolocationService, SSLService
from datetime import datetime

router = APIRouter()
dns_service = DNSService()
whois_service = WHOISService()
geo_service = GeolocationService()
ssl_service = SSLService()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ExposeChain"
    }


@router.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "ExposeChain API",
        "version": "1.0.0",
        "description": "AI-Powered Attack Surface & Threat Intelligence Platform",
        "endpoints": {
            "health": "/health",
            "scan": "/api/scan",
            "dns_lookup": "/api/dns/{domain}",
            "whois_lookup": "/api/whois/{domain}",
            "ssl_check": "/api/ssl/{domain}"
        }
    }


@router.post("/api/scan", response_model=ScanResponse)
async def scan_target(request: ScanRequest):
    """
    Main scanning endpoint with DNS, WHOIS, Geolocation, and SSL

    Args:
        request: ScanRequest containing target domain and scan_type

    Returns:
        ScanResponse with comprehensive scan results
    """
    try:
        # Detect target type (always domain)
        target_type = detect_target_type(request.target)

        # Initialize data dictionary
        scan_data = {
            "scan_initiated": datetime.utcnow().isoformat(),
            "scan_type": request.scan_type,
        }

        # Perform DNS lookup
        dns_results = dns_service.comprehensive_dns_lookup(request.target, target_type)
        scan_data["dns_lookup"] = dns_results

        # For domains, lookup all IPs found in DNS for geolocation
        geo_results = geo_service.lookup_domain_ips(dns_results)
        if geo_results.get('total_ips', 0) > 0:
            scan_data["geolocation"] = geo_results
            # Add hosting pattern analysis
            scan_data["hosting_analysis"] = geo_service.analyze_hosting_pattern(geo_results)

        # SSL Certificate check
        ssl_results = ssl_service.get_certificate(request.target)
        scan_data["ssl_certificate"] = ssl_results

        # Add SSL security analysis if certificate was retrieved
        if ssl_results.get("success"):
            scan_data["ssl_security_analysis"] = ssl_service.analyze_certificate_security(ssl_results)
            scan_data["hostname_validation"] = ssl_service.check_hostname_match(request.target, ssl_results)

        # Perform WHOIS lookup
        whois_results = whois_service.lookup_whois(request.target)
        scan_data["whois_lookup"] = whois_results

        # Add domain analysis
        if whois_results.get("success"):
            scan_data["domain_analysis"] = whois_service.analyze_domain_status(whois_results)

        message = f"Complete security scan finished for domain: {request.target}"

        return ScanResponse(
            success=True,
            target=request.target,
            target_type=target_type,
            message=message,
            data=scan_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )


@router.get("/api/dns/{target}")
async def dns_lookup(target: str):
    """
    Dedicated DNS lookup endpoint

    Args:
        target: Domain name

    Returns:
        DNS lookup results
    """
    try:
        target_type = detect_target_type(target)
        results = dns_service.comprehensive_dns_lookup(target, target_type)

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DNS lookup failed: {str(e)}"
        )


@router.get("/api/whois/{domain}")
async def whois_lookup(domain: str):
    """
    Dedicated WHOIS lookup endpoint

    Args:
        domain: Domain name to query

    Returns:
        WHOIS lookup results with domain analysis
    """
    try:
        whois_results = whois_service.lookup_whois(domain)

        analysis = None
        if whois_results.get("success"):
            analysis = whois_service.analyze_domain_status(whois_results)

        return {
            "success": whois_results.get("success", False),
            "whois_data": whois_results,
            "domain_analysis": analysis
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"WHOIS lookup failed: {str(e)}"
        )


@router.get("/api/ssl/{domain}")
async def ssl_certificate_check(domain: str, port: int = 443):
    """
    Dedicated SSL certificate check endpoint

    Args:
        domain: Domain name to check
        port: Port number (default: 443)

    Returns:
        SSL certificate information and security analysis
    """
    try:
        cert_data = ssl_service.get_certificate(domain, port)

        security_analysis = None
        hostname_validation = None

        if cert_data.get("success"):
            security_analysis = ssl_service.analyze_certificate_security(cert_data)
            hostname_validation = ssl_service.check_hostname_match(domain, cert_data)

        return {
            "success": cert_data.get("success", False),
            "certificate": cert_data,
            "security_analysis": security_analysis,
            "hostname_validation": hostname_validation
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SSL check failed: {str(e)}"
        )
