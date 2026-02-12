"""
Pydantic models for input validation
"""
from pydantic import BaseModel, Field, validator
from typing import Literal
import re
import ipaddress
import validators


class ScanRequest(BaseModel):
    """Request model for security scan"""
    
    target: str = Field(..., description="Target domain or IP address")
    scan_type: Literal["quick", "full"] = Field(
        default="quick", 
        description="Scan depth: quick or full"
    )
    
    @validator("target")
    def validate_target(cls, v):
        """Validate if input is a valid domain or IP address"""
        v = v.strip().lower()
        
        # Check if it's a valid IP address (IPv4 or IPv6)
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        # Check if it's a valid domain
        if validators.domain(v):
            return v
        
        # If neither, raise error
        raise ValueError(
            f"Invalid target: '{v}'. Must be a valid domain name or IP address."
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "target": "example.com",
                "scan_type": "quick"
            }
        }


class ScanResponse(BaseModel):
    """Response model for scan results"""
    
    success: bool
    target: str
    target_type: Literal["domain", "ipv4", "ipv6"]
    message: str
    data: dict = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "target": "example.com",
                "target_type": "domain",
                "message": "Scan completed successfully",
                "data": {}
            }
        }
