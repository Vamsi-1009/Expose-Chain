"""
WHOIS Lookup Service for ExposeChain
Handles WHOIS queries and domain registration data
"""
import whois
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from cachetools import TTLCache

logger = logging.getLogger("exposechain")


class WHOISService:
    """Service for WHOIS lookups and domain registration analysis"""

    def __init__(self):
        self._cache = TTLCache(maxsize=128, ttl=300)  # 5 min TTL

    def lookup_whois(self, domain: str) -> Dict[str, Any]:
        """
        Perform WHOIS lookup for a domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary with WHOIS results
        """
        cache_key = f"whois:{domain}"
        if cache_key in self._cache:
            logger.debug("Cache hit for %s", cache_key)
            return self._cache[cache_key]

        try:
            # Perform WHOIS lookup
            w = whois.whois(domain)
            
            # Extract and format data
            result = {
                "success": True,
                "domain": domain,
                "registrar": self._safe_get(w, 'registrar'),
                "creation_date": self._format_date(self._safe_get(w, 'creation_date')),
                "expiration_date": self._format_date(self._safe_get(w, 'expiration_date')),
                "updated_date": self._format_date(self._safe_get(w, 'updated_date')),
                "status": self._safe_get_list(w, 'status'),
                "name_servers": self._safe_get_list(w, 'name_servers'),
                "registrant": {
                    "name": self._safe_get(w, 'name'),
                    "organization": self._safe_get(w, 'org'),
                    "country": self._safe_get(w, 'country'),
                    "state": self._safe_get(w, 'state'),
                    "city": self._safe_get(w, 'city')
                },
                "contacts": {
                    "registrant_email": self._safe_get(w, 'emails'),
                }
            }
            
            # Calculate domain age
            if result["creation_date"]:
                result["domain_age_days"] = self._calculate_age(result["creation_date"])
            
            # Calculate days until expiration
            if result["expiration_date"]:
                result["days_until_expiration"] = self._calculate_days_until(result["expiration_date"])

            self._cache[cache_key] = result
            return result
            
        except Exception as e:
            return {
                "success": False,
                "domain": domain,
                "error": str(e),
                "message": "WHOIS lookup failed. Domain may not exist or WHOIS data unavailable."
            }
    
    def _safe_get(self, whois_obj: Any, key: str) -> Optional[str]:
        """
        Safely get a value from WHOIS object
        
        Args:
            whois_obj: WHOIS object
            key: Key to retrieve
            
        Returns:
            Value or None
        """
        try:
            value = getattr(whois_obj, key, None)
            if value is None:
                return None
            
            # Handle lists - return first item
            if isinstance(value, list):
                return str(value[0]) if value else None
            
            return str(value) if value else None
        except:
            return None
    
    def _safe_get_list(self, whois_obj: Any, key: str) -> list:
        """
        Safely get a list value from WHOIS object
        
        Args:
            whois_obj: WHOIS object
            key: Key to retrieve
            
        Returns:
            List of values or empty list
        """
        try:
            value = getattr(whois_obj, key, None)
            if value is None:
                return []
            
            # Ensure it's a list
            if isinstance(value, list):
                # Clean up the list - remove None and convert to strings
                return [str(item).lower() for item in value if item]
            
            # If single value, make it a list
            return [str(value).lower()] if value else []
        except:
            return []
    
    def _format_date(self, date_value: Any) -> Optional[str]:
        """
        Format date value to ISO string
        
        Args:
            date_value: Date value from WHOIS
            
        Returns:
            ISO formatted date string or None
        """
        try:
            if date_value is None:
                return None
            
            # Handle list of dates - use first one
            if isinstance(date_value, list):
                date_value = date_value[0] if date_value else None
            
            if date_value is None:
                return None
            
            # If already datetime object
            if isinstance(date_value, datetime):
                return date_value.isoformat()
            
            # If string, try to parse
            if isinstance(date_value, str):
                return date_value
            
            return str(date_value)
        except:
            return None
    
    def _calculate_age(self, creation_date: str) -> Optional[int]:
        """
        Calculate domain age in days
        
        Args:
            creation_date: ISO formatted creation date
            
        Returns:
            Age in days or None
        """
        try:
            created = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
            age = (datetime.now(created.tzinfo) - created).days
            return age
        except:
            return None
    
    def _calculate_days_until(self, expiration_date: str) -> Optional[int]:
        """
        Calculate days until expiration
        
        Args:
            expiration_date: ISO formatted expiration date
            
        Returns:
            Days until expiration (negative if expired) or None
        """
        try:
            expires = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
            days = (expires - datetime.now(expires.tzinfo)).days
            return days
        except:
            return None
    
    def analyze_domain_status(self, whois_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze domain status and provide insights
        
        Args:
            whois_data: WHOIS lookup result
            
        Returns:
            Analysis results
        """
        if not whois_data.get("success"):
            return {
                "status": "unknown",
                "risk_level": "unknown",
                "insights": []
            }
        
        insights = []
        risk_level = "low"
        
        # Check domain age
        age = whois_data.get("domain_age_days")
        if age is not None:
            if age < 30:
                insights.append("Very new domain (less than 30 days old)")
                risk_level = "medium"
            elif age < 180:
                insights.append("Relatively new domain (less than 6 months old)")
            elif age > 3650:
                insights.append("Well-established domain (over 10 years old)")
        
        # Check expiration
        days_until_exp = whois_data.get("days_until_expiration")
        if days_until_exp is not None:
            if days_until_exp < 0:
                insights.append("Domain has expired!")
                risk_level = "high"
            elif days_until_exp < 30:
                insights.append("Domain expires soon (less than 30 days)")
                risk_level = "medium"
            elif days_until_exp < 90:
                insights.append("Domain expires in less than 90 days")
        
        # Check privacy protection
        registrant_name = whois_data.get("registrant", {}).get("name")
        if registrant_name and "privacy" in registrant_name.lower():
            insights.append("Domain uses privacy protection service")
        
        # Check status
        status_list = whois_data.get("status", [])
        if any("lock" in status.lower() for status in status_list):
            insights.append("Domain has transfer/update locks (good security)")
        
        return {
            "status": "active" if days_until_exp and days_until_exp > 0 else "expired",
            "risk_level": risk_level,
            "insights": insights,
            "domain_age_days": age,
            "days_until_expiration": days_until_exp
        }
