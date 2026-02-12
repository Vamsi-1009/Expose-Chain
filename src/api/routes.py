"""
API Routes for ExposeChain
"""
from fastapi import APIRouter, HTTPException
from src.models import ScanRequest, ScanResponse
from src.utils import detect_target_type
from src.services import DNSService, WHOISService, GeolocationService
from datetime import datetime

router = APIRouter()
dns_service = DNSService()
whois_service = WHOISService()
geo_service = GeolocationService()


@router.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ExposeChain API",
        "version": "1.0.0",
        "description": "AI-Powered Attack Surface & Threat Intelligence Platform",
        "endpoints": {
            "health": "/health",
            "scan": "/api/scan",
            "dns_lookup": "/api/dns/{target}",
            "whois_lookup": "/api/whois/{domain}",
            "geolocation": "/api/geo/{ip}"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ExposeChain"
    }


@router.post("/api/scan", response_model=ScanResponse)
async def scan_target(request: ScanRequest):
    """
    Main scanning endpoint with DNS, WHOIS, and Geolocation
    
    Args:
        request: ScanRequest containing target and scan_type
        
    Returns:
        ScanResponse with comprehensive scan results
    """
    try:
        # Detect target type
        target_type = detect_target_type(request.target)
        
        # Initialize data dictionary
        scan_data = {
            "scan_initiated": datetime.utcnow().isoformat(),
            "scan_type": request.scan_type,
        }
        
        # Perform DNS lookup
        dns_results = dns_service.comprehensive_dns_lookup(request.target, target_type)
        scan_data["dns_lookup"] = dns_results
        
        # Perform geolocation lookup
        if target_type == "domain":
            # For domains, lookup all IPs found in DNS
            geo_results = geo_service.lookup_domain_ips(dns_results)
            if geo_results.get('total_ips', 0) > 0:
                scan_data["geolocation"] = geo_results
                # Add hosting pattern analysis
                scan_data["hosting_analysis"] = geo_service.analyze_hosting_pattern(geo_results)
        elif target_type in ["ipv4", "ipv6"]:
            # For IPs, direct geolocation lookup
            geo_result = geo_service.lookup_ip_location(request.target)
            scan_data["geolocation"] = {
                "total_ips": 1,
                "ip_locations": {request.target: geo_result}
            }
        
        # Perform WHOIS lookup for domains (after geolocation to minimize wait time)
        if target_type == "domain":
            whois_results = whois_service.lookup_whois(request.target)
            scan_data["whois_lookup"] = whois_results
            
            # Add domain analysis
            if whois_results.get("success"):
                scan_data["domain_analysis"] = whois_service.analyze_domain_status(whois_results)
        
        # Build response message
        if target_type == "domain":
            message = f"Complete scan finished for domain: {request.target}"
        else:
            message = f"Geolocation and reverse DNS completed for {target_type}: {request.target}"
        
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
        target: Domain name or IP address
        
    Returns:
        DNS lookup results
    """
    try:
        # Detect target type
        target_type = detect_target_type(target)
        
        # Perform DNS lookup
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
        # Perform WHOIS lookup
        whois_results = whois_service.lookup_whois(domain)
        
        # Add analysis if successful
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


@router.get("/api/geo/{ip}")
async def geolocation_lookup(ip: str):
    """
    Dedicated geolocation lookup endpoint
    
    Args:
        ip: IP address to lookup
        
    Returns:
        Geolocation results
    """
    try:
        # Perform geolocation lookup
        geo_result = geo_service.lookup_ip_location(ip)
        
        return {
            "success": geo_result.get("success", False),
            "geolocation": geo_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Geolocation lookup failed: {str(e)}"
        )
