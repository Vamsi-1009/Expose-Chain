"""
DNS Lookup Service for ExposeChain
Handles DNS queries and analysis
"""
import dns.resolver
import dns.reversename
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from cachetools import TTLCache

logger = logging.getLogger("exposechain")


class DNSService:
    """Service for DNS lookups and analysis"""

    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        # Use Google's DNS servers for reliability
        self.resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        self.resolver.timeout = 5
        self.resolver.lifetime = 5
        self._cache = TTLCache(maxsize=128, ttl=300)  # 5 min TTL
    
    def lookup_a_records(self, domain: str) -> Dict[str, Any]:
        """
        Get A (IPv4) records for a domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary with A record results
        """
        try:
            start_time = time.time()
            answers = self.resolver.resolve(domain, 'A')
            query_time = round((time.time() - start_time) * 1000, 2)
            
            records = []
            for rdata in answers:
                records.append({
                    "ip": str(rdata),
                    "ttl": answers.rrset.ttl
                })
            
            return {
                "success": True,
                "record_type": "A",
                "records": records,
                "query_time_ms": query_time,
                "count": len(records)
            }
        except dns.resolver.NoAnswer:
            return {
                "success": False,
                "record_type": "A",
                "error": "No A records found",
                "records": []
            }
        except dns.resolver.NXDOMAIN:
            return {
                "success": False,
                "record_type": "A",
                "error": "Domain does not exist",
                "records": []
            }
        except Exception as e:
            return {
                "success": False,
                "record_type": "A",
                "error": str(e),
                "records": []
            }
    
    def lookup_aaaa_records(self, domain: str) -> Dict[str, Any]:
        """
        Get AAAA (IPv6) records for a domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary with AAAA record results
        """
        try:
            start_time = time.time()
            answers = self.resolver.resolve(domain, 'AAAA')
            query_time = round((time.time() - start_time) * 1000, 2)
            
            records = []
            for rdata in answers:
                records.append({
                    "ip": str(rdata),
                    "ttl": answers.rrset.ttl
                })
            
            return {
                "success": True,
                "record_type": "AAAA",
                "records": records,
                "query_time_ms": query_time,
                "count": len(records)
            }
        except dns.resolver.NoAnswer:
            return {
                "success": False,
                "record_type": "AAAA",
                "error": "No AAAA records found",
                "records": []
            }
        except Exception as e:
            return {
                "success": False,
                "record_type": "AAAA",
                "error": str(e),
                "records": []
            }
    
    def lookup_mx_records(self, domain: str) -> Dict[str, Any]:
        """
        Get MX (Mail Exchange) records for a domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary with MX record results
        """
        try:
            start_time = time.time()
            answers = self.resolver.resolve(domain, 'MX')
            query_time = round((time.time() - start_time) * 1000, 2)
            
            records = []
            for rdata in answers:
                records.append({
                    "priority": rdata.preference,
                    "mail_server": str(rdata.exchange).rstrip('.'),
                    "ttl": answers.rrset.ttl
                })
            
            # Sort by priority (lower is higher priority)
            records.sort(key=lambda x: x['priority'])
            
            return {
                "success": True,
                "record_type": "MX",
                "records": records,
                "query_time_ms": query_time,
                "count": len(records)
            }
        except dns.resolver.NoAnswer:
            return {
                "success": False,
                "record_type": "MX",
                "error": "No MX records found",
                "records": []
            }
        except Exception as e:
            return {
                "success": False,
                "record_type": "MX",
                "error": str(e),
                "records": []
            }
    
    def lookup_ns_records(self, domain: str) -> Dict[str, Any]:
        """
        Get NS (Name Server) records for a domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary with NS record results
        """
        try:
            start_time = time.time()
            answers = self.resolver.resolve(domain, 'NS')
            query_time = round((time.time() - start_time) * 1000, 2)
            
            records = []
            for rdata in answers:
                records.append({
                    "nameserver": str(rdata).rstrip('.'),
                    "ttl": answers.rrset.ttl
                })
            
            return {
                "success": True,
                "record_type": "NS",
                "records": records,
                "query_time_ms": query_time,
                "count": len(records)
            }
        except dns.resolver.NoAnswer:
            return {
                "success": False,
                "record_type": "NS",
                "error": "No NS records found",
                "records": []
            }
        except Exception as e:
            return {
                "success": False,
                "record_type": "NS",
                "error": str(e),
                "records": []
            }
    
    def lookup_txt_records(self, domain: str) -> Dict[str, Any]:
        """
        Get TXT records for a domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary with TXT record results
        """
        try:
            start_time = time.time()
            answers = self.resolver.resolve(domain, 'TXT')
            query_time = round((time.time() - start_time) * 1000, 2)
            
            records = []
            for rdata in answers:
                # TXT records can have multiple strings
                txt_data = ' '.join([s.decode('utf-8') if isinstance(s, bytes) else s for s in rdata.strings])
                records.append({
                    "data": txt_data,
                    "ttl": answers.rrset.ttl
                })
            
            return {
                "success": True,
                "record_type": "TXT",
                "records": records,
                "query_time_ms": query_time,
                "count": len(records)
            }
        except dns.resolver.NoAnswer:
            return {
                "success": False,
                "record_type": "TXT",
                "error": "No TXT records found",
                "records": []
            }
        except Exception as e:
            return {
                "success": False,
                "record_type": "TXT",
                "error": str(e),
                "records": []
            }
    
    def reverse_dns_lookup(self, ip_address: str) -> Dict[str, Any]:
        """
        Perform reverse DNS lookup for an IP address
        
        Args:
            ip_address: IP address to lookup
            
        Returns:
            Dictionary with reverse DNS results
        """
        try:
            start_time = time.time()
            addr = dns.reversename.from_address(ip_address)
            answers = self.resolver.resolve(addr, 'PTR')
            query_time = round((time.time() - start_time) * 1000, 2)
            
            hostnames = [str(rdata).rstrip('.') for rdata in answers]
            
            return {
                "success": True,
                "ip": ip_address,
                "hostnames": hostnames,
                "query_time_ms": query_time
            }
        except Exception as e:
            return {
                "success": False,
                "ip": ip_address,
                "error": str(e),
                "hostnames": []
            }
    
    def comprehensive_dns_lookup(self, target: str, target_type: str) -> Dict[str, Any]:
        """
        Perform comprehensive DNS lookup for a target

        Args:
            target: Domain name or IP address
            target_type: Type of target (domain, ipv4, ipv6)

        Returns:
            Dictionary with all DNS results
        """
        cache_key = f"dns:{target}:{target_type}"
        if cache_key in self._cache:
            logger.debug("Cache hit for %s", cache_key)
            return self._cache[cache_key]

        results = {
            "target": target,
            "target_type": target_type,
            "timestamp": datetime.utcnow().isoformat(),
            "dns_records": {}
        }
        
        if target_type == "domain":
            # Query all record types for domains
            results["dns_records"]["A"] = self.lookup_a_records(target)
            results["dns_records"]["AAAA"] = self.lookup_aaaa_records(target)
            results["dns_records"]["MX"] = self.lookup_mx_records(target)
            results["dns_records"]["NS"] = self.lookup_ns_records(target)
            results["dns_records"]["TXT"] = self.lookup_txt_records(target)
            
            # Calculate total query time
            total_time = sum([
                results["dns_records"]["A"].get("query_time_ms", 0),
                results["dns_records"]["AAAA"].get("query_time_ms", 0),
                results["dns_records"]["MX"].get("query_time_ms", 0),
                results["dns_records"]["NS"].get("query_time_ms", 0),
                results["dns_records"]["TXT"].get("query_time_ms", 0)
            ])
            results["total_query_time_ms"] = round(total_time, 2)
            
        elif target_type in ["ipv4", "ipv6"]:
            # Perform reverse DNS lookup for IP addresses
            results["reverse_dns"] = self.reverse_dns_lookup(target)

        self._cache[cache_key] = results
        return results
