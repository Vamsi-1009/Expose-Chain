"""
Geolocation Service for ExposeChain
Handles IP geolocation lookups using free public APIs
"""
import requests
from typing import Dict, Any, Optional
import time


class GeolocationService:
    """Service for IP geolocation lookups"""
    
    def __init__(self):
        # We'll use ip-api.com (free, no API key required)
        # Limit: 45 requests per minute
        self.api_url = "http://ip-api.com/json/{ip}"
        self.timeout = 10
    
    def lookup_ip_location(self, ip_address: str) -> Dict[str, Any]:
        """
        Get geolocation information for an IP address
        
        Args:
            ip_address: IP address to lookup
            
        Returns:
            Dictionary with geolocation results
        """
        try:
            # Query the API
            url = self.api_url.format(ip=ip_address)
            
            # Add fields parameter to get all available data
            params = {
                'fields': 'status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query'
            }
            
            start_time = time.time()
            response = requests.get(url, params=params, timeout=self.timeout)
            query_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if lookup was successful
                if data.get('status') == 'success':
                    return {
                        "success": True,
                        "ip": ip_address,
                        "location": {
                            "continent": data.get('continent'),
                            "continent_code": data.get('continentCode'),
                            "country": data.get('country'),
                            "country_code": data.get('countryCode'),
                            "region": data.get('regionName'),
                            "region_code": data.get('region'),
                            "city": data.get('city'),
                            "district": data.get('district'),
                            "zip_code": data.get('zip'),
                            "timezone": data.get('timezone'),
                            "currency": data.get('currency')
                        },
                        "coordinates": {
                            "latitude": data.get('lat'),
                            "longitude": data.get('lon')
                        },
                        "network": {
                            "isp": data.get('isp'),
                            "organization": data.get('org'),
                            "as_number": data.get('as'),
                            "as_name": data.get('asname')
                        },
                        "flags": {
                            "is_mobile": data.get('mobile', False),
                            "is_proxy": data.get('proxy', False),
                            "is_hosting": data.get('hosting', False)
                        },
                        "reverse_dns": data.get('reverse'),
                        "query_time_ms": query_time
                    }
                else:
                    # API returned failure status
                    return {
                        "success": False,
                        "ip": ip_address,
                        "error": data.get('message', 'Geolocation lookup failed'),
                        "query_time_ms": query_time
                    }
            else:
                return {
                    "success": False,
                    "ip": ip_address,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query_time_ms": query_time
                }
                
        except requests.Timeout:
            return {
                "success": False,
                "ip": ip_address,
                "error": "Request timeout (>10 seconds)"
            }
        except Exception as e:
            return {
                "success": False,
                "ip": ip_address,
                "error": str(e)
            }
    
    def lookup_domain_ips(self, dns_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lookup geolocation for all IPs found in DNS results
        
        Args:
            dns_results: DNS lookup results containing A and AAAA records
            
        Returns:
            Dictionary with geolocation for all IPs
        """
        locations = {}
        
        # Get A records (IPv4)
        a_records = dns_results.get('dns_records', {}).get('A', {})
        if a_records.get('success'):
            for record in a_records.get('records', []):
                ip = record.get('ip')
                if ip and ip not in locations:
                    locations[ip] = self.lookup_ip_location(ip)
        
        # Get AAAA records (IPv6)
        aaaa_records = dns_results.get('dns_records', {}).get('AAAA', {})
        if aaaa_records.get('success'):
            for record in aaaa_records.get('records', []):
                ip = record.get('ip')
                if ip and ip not in locations:
                    locations[ip] = self.lookup_ip_location(ip)
        
        return {
            "total_ips": len(locations),
            "ip_locations": locations
        }
    
    def analyze_hosting_pattern(self, geolocation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze hosting patterns from geolocation data
        
        Args:
            geolocation_data: Geolocation lookup results
            
        Returns:
            Analysis of hosting patterns
        """
        ip_locations = geolocation_data.get('ip_locations', {})
        
        if not ip_locations:
            return {
                "pattern": "No IP data available",
                "insights": []
            }
        
        countries = set()
        cities = set()
        isps = set()
        hosting_count = 0
        proxy_count = 0
        cdn_keywords = ['cloudflare', 'akamai', 'fastly', 'amazon', 'google', 'microsoft', 'azure']
        is_cdn = False
        
        insights = []
        
        for ip, data in ip_locations.items():
            if data.get('success'):
                # Collect countries
                country = data.get('location', {}).get('country')
                if country:
                    countries.add(country)
                
                # Collect cities
                city = data.get('location', {}).get('city')
                if city:
                    cities.add(city)
                
                # Collect ISPs
                isp = data.get('network', {}).get('isp')
                if isp:
                    isps.add(isp)
                    # Check for CDN
                    if any(keyword in isp.lower() for keyword in cdn_keywords):
                        is_cdn = True
                
                # Check flags
                if data.get('flags', {}).get('is_hosting'):
                    hosting_count += 1
                if data.get('flags', {}).get('is_proxy'):
                    proxy_count += 1
        
        # Generate insights
        if len(countries) > 1:
            insights.append(f"Multi-country deployment: Servers in {len(countries)} countries")
        elif len(countries) == 1:
            insights.append(f"Single country deployment: {list(countries)[0]}")
        
        if is_cdn:
            insights.append("Using CDN/Cloud provider")
        
        if hosting_count == len(ip_locations):
            insights.append("All IPs are from hosting/datacenter providers")
        
        if proxy_count > 0:
            insights.append(f"Proxy/VPN detected on {proxy_count} IP(s)")
        
        return {
            "pattern": "CDN/Distributed" if is_cdn or len(countries) > 1 else "Centralized",
            "countries": list(countries),
            "cities": list(cities),
            "isps": list(isps),
            "insights": insights,
            "is_cdn": is_cdn,
            "hosting_provider_count": hosting_count
        }
