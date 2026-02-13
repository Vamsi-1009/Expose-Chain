"""
Pydantic models for input validation
"""
from pydantic import BaseModel, Field, validator
from typing import Literal
import validators


class ScanRequest(BaseModel):
    """Request model for security scan"""

    target: str = Field(..., description="Target domain name")
    scan_type: Literal["quick", "full"] = Field(
        default="quick",
        description="Scan depth: quick or full"
    )

    @validator("target")
    def validate_target(cls, v):
        """Validate if input is a valid domain name"""
        v = v.strip().lower()

        # Check if it's a valid domain
        if validators.domain(v):
            return v

        # If not a valid domain, raise error
        raise ValueError(
            f"Invalid target: '{v}'. Must be a valid domain name (e.g., example.com)."
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
    target_type: Literal["domain"] = "domain"
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
