"""
API Routes for ExposeChain
Async endpoints with rate limiting and AI analysis (No Database)
"""
import asyncio
import uuid
import logging
from fastapi import APIRouter, HTTPException, Request
from src.models import ScanRequest, ScanResponse
from src.utils import detect_target_type
from src.services import DNSService, WHOISService, GeolocationService, SSLService, AIRiskPredictor
from src.utils.rate_limiter import limiter
from datetime import datetime

logger = logging.getLogger("exposechain")

router = APIRouter()
dns_service = DNSService()
whois_service = WHOISService()
geo_service = GeolocationService()
ssl_service = SSLService()
ai_predictor = AIRiskPredictor()


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
            "ssl_check": "/api/ssl/{domain}",
            "geo_lookup": "/api/geo/{ip}",
            "history": "/api/history",
            "report": "/api/report/{scan_id}"
        }
    }


@router.post("/api/scan", response_model=ScanResponse)
@limiter.limit("10/minute")
async def scan_target(request: Request, scan_request: ScanRequest):
    """
    Main scanning endpoint with DNS, WHOIS, Geolocation, SSL, and AI Analysis.
    Runs DNS, WHOIS, and SSL lookups in parallel for faster results.
    """
    try:
        target_type = detect_target_type(scan_request.target)

        scan_data = {
            "scan_initiated": datetime.utcnow().isoformat(),
            "scan_type": scan_request.scan_type,
        }

        # Run DNS, WHOIS, and SSL lookups in parallel
        dns_results, whois_results, ssl_results = await asyncio.gather(
            asyncio.to_thread(dns_service.comprehensive_dns_lookup, scan_request.target, target_type),
            asyncio.to_thread(whois_service.lookup_whois, scan_request.target),
            asyncio.to_thread(ssl_service.get_certificate, scan_request.target),
        )

        scan_data["dns_lookup"] = dns_results

        # Geolocation depends on DNS results, run after DNS
        geo_results = await asyncio.to_thread(geo_service.lookup_domain_ips, dns_results)
        if geo_results.get('total_ips', 0) > 0:
            scan_data["geolocation"] = geo_results
            scan_data["hosting_analysis"] = geo_service.analyze_hosting_pattern(geo_results)

        scan_data["ssl_certificate"] = ssl_results
        if ssl_results.get("success"):
            scan_data["ssl_security_analysis"] = ssl_service.analyze_certificate_security(ssl_results)
            scan_data["hostname_validation"] = ssl_service.check_hostname_match(scan_request.target, ssl_results)

        scan_data["whois_lookup"] = whois_results
        if whois_results.get("success"):
            scan_data["domain_analysis"] = whois_service.analyze_domain_status(whois_results)

        # AI Risk Analysis
        ai_analysis = ai_predictor.analyze(scan_data)
        scan_data["ai_analysis"] = ai_analysis

        # Generate scan ID (for reference, but not saved anywhere)
        scan_id = str(uuid.uuid4())
        scan_data["scan_id"] = scan_id

        message = f"Complete security scan finished for domain: {scan_request.target}"

        logger.info("Scan completed: id=%s target=%s", scan_id, scan_request.target)

        return ScanResponse(
            success=True,
            target=scan_request.target,
            target_type=target_type,
            message=message,
            data=scan_data
        )

    except Exception as e:
        logger.error("Scan failed for target %s: %s", scan_request.target, str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your scan. Please try again."
        )


@router.get("/api/dns/{target}")
@limiter.limit("20/minute")
async def dns_lookup(request: Request, target: str):
    """Dedicated DNS lookup endpoint"""
    try:
        target_type = detect_target_type(target)
        results = await asyncio.to_thread(dns_service.comprehensive_dns_lookup, target, target_type)
        return {"success": True, "results": results}
    except Exception as e:
        logger.error("DNS lookup failed for %s: %s", target, str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="DNS lookup failed. Please try again."
        )


@router.get("/api/whois/{domain}")
@limiter.limit("20/minute")
async def whois_lookup(request: Request, domain: str):
    """Dedicated WHOIS lookup endpoint"""
    try:
        whois_results = await asyncio.to_thread(whois_service.lookup_whois, domain)

        analysis = None
        if whois_results.get("success"):
            analysis = whois_service.analyze_domain_status(whois_results)

        return {
            "success": whois_results.get("success", False),
            "whois_data": whois_results,
            "domain_analysis": analysis
        }
    except Exception as e:
        logger.error("WHOIS lookup failed for %s: %s", domain, str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="WHOIS lookup failed. Please try again."
        )


@router.get("/api/ssl/{domain}")
@limiter.limit("20/minute")
async def ssl_certificate_check(request: Request, domain: str, port: int = 443):
    """Dedicated SSL certificate check endpoint"""
    try:
        cert_data = await asyncio.to_thread(ssl_service.get_certificate, domain, port)

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
        logger.error("SSL check failed for %s: %s", domain, str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="SSL check failed. Please try again."
        )


# Database endpoints removed - no persistence needed
# Scans return fresh results every time
