"""
AI Risk Prediction Service for ExposeChain
Rule-based weighted scoring model for threat assessment

Pipeline: Feature extraction -> Weighted scoring -> Category classification -> NL report

The model extracts features from scan data across 4 dimensions:
- Domain maturity (WHOIS age, expiration, privacy)
- SSL/TLS security (score, protocol, key strength, expiry)
- Infrastructure (hosting patterns, CDN, proxy/VPN usage)
- DNS profile (record diversity, SPF/DMARC presence)

Each feature contributes a weighted score. The aggregate determines
the threat category and confidence level.
"""
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger("exposechain")


class AIRiskPredictor:
    """
    AI-powered risk prediction using feature extraction and weighted scoring.

    Analyzes scan data to produce:
    - Risk score (0-100)
    - Threat category (legitimate, suspicious, malware_hosting, phishing)
    - Confidence level (0.0-1.0)
    - Natural language threat assessment
    - Actionable recommendations
    """

    # Weight configuration for each feature dimension
    WEIGHTS = {
        "domain_age": 0.15,
        "domain_expiration": 0.08,
        "domain_privacy": 0.05,
        "ssl_score": 0.18,
        "ssl_protocol": 0.08,
        "ssl_expiry": 0.06,
        "ssl_present": 0.10,
        "infra_proxy": 0.10,
        "infra_hosting": 0.03,
        "infra_diversity": 0.02,
        "dns_spf": 0.05,
        "dns_dmarc": 0.04,
        "dns_record_count": 0.03,
        "dns_mx_present": 0.03,
    }

    # Threat categories with score ranges
    CATEGORIES = {
        "legitimate": {"min_score": 0, "max_score": 20, "label": "Legitimate"},
        "suspicious": {"min_score": 21, "max_score": 50, "label": "Suspicious"},
        "malware_hosting": {"min_score": 51, "max_score": 75, "label": "Potential Malware Hosting"},
        "phishing": {"min_score": 76, "max_score": 100, "label": "Likely Phishing / Malicious"},
    }

    def analyze(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: analyze scan data and produce threat assessment.

        Args:
            scan_data: Complete scan results from all services

        Returns:
            Dictionary with risk_score, risk_level, threat_category,
            confidence, features, factors, assessment, recommendations
        """
        logger.info("Running AI risk analysis")

        features = self._extract_features(scan_data)
        score, factors = self._calculate_score(features)
        category = self._classify_threat(score, features)
        confidence = self._calculate_confidence(features)
        assessment = self._generate_assessment(score, category, features, factors)
        recommendations = self._generate_recommendations(score, category, features)

        risk_level = (
            "low" if score <= 20
            else "medium" if score <= 45
            else "high" if score <= 70
            else "critical"
        )

        result = {
            "overall_risk_score": score,
            "threat_level": risk_level,
            "threat_category": category,
            "confidence": round(confidence, 2),
            "threats_detected": factors,  # Frontend expects threats_detected
            "recommendations": recommendations,
            "summary": assessment,  # Frontend expects summary
            "features": features,
            "model_version": "1.0.0",
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "AI analysis complete: score=%d, level=%s, category=%s, confidence=%.2f",
            score, risk_level, category, confidence
        )

        return result

    def _extract_features(self, data: Dict) -> Dict[str, Any]:
        """Extract numerical and categorical features from raw scan data"""
        features = {}

        # --- Domain features from WHOIS ---
        whois = data.get("whois_lookup", {})
        features["domain_age_days"] = whois.get("domain_age_days")
        features["days_until_expiration"] = whois.get("days_until_expiration")
        features["has_privacy_protection"] = (
            "privacy" in (whois.get("registrant", {}).get("name") or "").lower()
        )
        features["whois_available"] = whois.get("success", False)

        da = data.get("domain_analysis", {})
        features["domain_status"] = da.get("status", "unknown")

        # --- SSL features ---
        ssl_cert = data.get("ssl_certificate", {})
        features["ssl_present"] = ssl_cert.get("success", False)

        sa = data.get("ssl_security_analysis", {})
        features["ssl_score"] = sa.get("security_score")
        features["ssl_risk_level"] = sa.get("risk_level", "unknown")

        ssl_details = sa.get("details", {})
        features["ssl_protocol"] = ssl_details.get("protocol_version", "")
        features["ssl_key_type"] = ssl_details.get("key_type", "")
        features["ssl_key_strength"] = ssl_details.get("key_strength", "")
        features["ssl_days_left"] = ssl_details.get("expires_in_days")
        features["ssl_valid"] = ssl_details.get("is_valid", False)

        # --- Infrastructure features ---
        geo = data.get("geolocation", {})
        features["total_ips"] = geo.get("total_ips", 0)

        ha = data.get("hosting_analysis", {})
        features["is_cdn"] = ha.get("is_cdn", False)
        features["hosting_pattern"] = ha.get("pattern", "")
        features["country_count"] = len(ha.get("countries", []))
        features["hosting_provider_count"] = ha.get("hosting_provider_count", 0)

        # Check for proxy/VPN in geo data
        proxy_count = 0
        ip_locations = geo.get("ip_locations", {})
        for ip, loc in ip_locations.items():
            if loc.get("success") and loc.get("flags", {}).get("is_proxy"):
                proxy_count += 1
        features["proxy_count"] = proxy_count

        # --- DNS features ---
        dns_data = data.get("dns_lookup", {})
        dns_records = dns_data.get("dns_records", {})
        features["dns_a_count"] = dns_records.get("A", {}).get("count", 0)
        features["dns_mx_present"] = dns_records.get("MX", {}).get("success", False)
        features["dns_ns_count"] = dns_records.get("NS", {}).get("count", 0)
        features["dns_txt_count"] = dns_records.get("TXT", {}).get("count", 0)

        # Check for SPF and DMARC in TXT records
        txt_records = dns_records.get("TXT", {}).get("records", [])
        txt_data = " ".join(r.get("data", "") for r in txt_records).lower()
        features["has_spf"] = "v=spf1" in txt_data
        features["has_dmarc"] = "_dmarc" in txt_data or "v=dmarc1" in txt_data

        return features

    def _calculate_score(self, features: Dict) -> Tuple[int, List[Dict]]:
        """Apply weighted scoring to features, returns (score, factors_list)"""
        raw_score = 0.0
        factors = []

        # --- Domain age scoring ---
        age = features.get("domain_age_days")
        if age is not None:
            if age < 30:
                pts = 100 * self.WEIGHTS["domain_age"]
                raw_score += pts
                factors.append({
                    "factor": "Very new domain (< 30 days)",
                    "points": round(pts, 1),
                    "severity": "high"
                })
            elif age < 180:
                pts = 60 * self.WEIGHTS["domain_age"]
                raw_score += pts
                factors.append({
                    "factor": "Relatively new domain (< 6 months)",
                    "points": round(pts, 1),
                    "severity": "medium"
                })
            elif age < 365:
                pts = 20 * self.WEIGHTS["domain_age"]
                raw_score += pts
                factors.append({
                    "factor": "Domain less than 1 year old",
                    "points": round(pts, 1),
                    "severity": "low"
                })
            # age > 365: established domain, no risk points
        else:
            pts = 40 * self.WEIGHTS["domain_age"]
            raw_score += pts
            factors.append({
                "factor": "Domain age unknown (WHOIS data unavailable)",
                "points": round(pts, 1),
                "severity": "medium"
            })

        # --- Domain expiration ---
        exp = features.get("days_until_expiration")
        if exp is not None:
            if exp < 0:
                pts = 100 * self.WEIGHTS["domain_expiration"]
                raw_score += pts
                factors.append({
                    "factor": "Domain has EXPIRED",
                    "points": round(pts, 1),
                    "severity": "critical"
                })
            elif exp < 30:
                pts = 70 * self.WEIGHTS["domain_expiration"]
                raw_score += pts
                factors.append({
                    "factor": "Domain expires within 30 days",
                    "points": round(pts, 1),
                    "severity": "high"
                })
            elif exp < 90:
                pts = 30 * self.WEIGHTS["domain_expiration"]
                raw_score += pts
                factors.append({
                    "factor": "Domain expires within 90 days",
                    "points": round(pts, 1),
                    "severity": "medium"
                })

        # --- Privacy protection ---
        if features.get("has_privacy_protection"):
            pts = 40 * self.WEIGHTS["domain_privacy"]
            raw_score += pts
            factors.append({
                "factor": "WHOIS privacy enabled (common for both legit and malicious)",
                "points": round(pts, 1),
                "severity": "low"
            })

        # --- SSL presence ---
        if not features.get("ssl_present"):
            pts = 100 * self.WEIGHTS["ssl_present"]
            raw_score += pts
            factors.append({
                "factor": "No SSL/TLS certificate detected",
                "points": round(pts, 1),
                "severity": "high"
            })

        # --- SSL score deficit ---
        ssl_score = features.get("ssl_score")
        if ssl_score is not None:
            deficit = max(0, 100 - ssl_score)
            pts = deficit * self.WEIGHTS["ssl_score"]
            if pts > 0:
                raw_score += pts
                factors.append({
                    "factor": f"SSL security score deficit ({ssl_score}/100)",
                    "points": round(pts, 1),
                    "severity": "medium" if ssl_score >= 70 else "high"
                })

        # --- SSL protocol version ---
        proto = features.get("ssl_protocol", "")
        if proto in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
            pts = 100 * self.WEIGHTS["ssl_protocol"]
            raw_score += pts
            factors.append({
                "factor": f"Outdated SSL/TLS protocol: {proto}",
                "points": round(pts, 1),
                "severity": "high"
            })

        # --- SSL expiry ---
        ssl_days = features.get("ssl_days_left")
        if ssl_days is not None and ssl_days < 7:
            pts = 80 * self.WEIGHTS["ssl_expiry"]
            raw_score += pts
            factors.append({
                "factor": f"SSL certificate expires in {ssl_days} days",
                "points": round(pts, 1),
                "severity": "high"
            })
        elif ssl_days is not None and ssl_days < 30:
            pts = 40 * self.WEIGHTS["ssl_expiry"]
            raw_score += pts
            factors.append({
                "factor": f"SSL certificate expires in {ssl_days} days",
                "points": round(pts, 1),
                "severity": "medium"
            })

        # --- Proxy/VPN detection ---
        proxy_count = features.get("proxy_count", 0)
        if proxy_count > 0:
            pts = min(100, proxy_count * 60) * self.WEIGHTS["infra_proxy"]
            raw_score += pts
            factors.append({
                "factor": f"Proxy/VPN detected on {proxy_count} IP(s)",
                "points": round(pts, 1),
                "severity": "medium"
            })

        # --- No SPF record ---
        if not features.get("has_spf"):
            pts = 60 * self.WEIGHTS["dns_spf"]
            raw_score += pts
            factors.append({
                "factor": "No SPF record (email spoofing possible)",
                "points": round(pts, 1),
                "severity": "medium"
            })

        # --- No DMARC record ---
        if not features.get("has_dmarc"):
            pts = 50 * self.WEIGHTS["dns_dmarc"]
            raw_score += pts
            factors.append({
                "factor": "No DMARC record (email authentication missing)",
                "points": round(pts, 1),
                "severity": "low"
            })

        # --- No MX records ---
        if not features.get("dns_mx_present"):
            pts = 30 * self.WEIGHTS["dns_mx_present"]
            raw_score += pts
            factors.append({
                "factor": "No MX records (no email infrastructure)",
                "points": round(pts, 1),
                "severity": "low"
            })

        final_score = min(100, max(0, round(raw_score)))
        return final_score, factors

    def _classify_threat(self, score: int, features: Dict) -> str:
        """Classify into threat category using score + heuristic rules"""
        # Heuristic overrides for known patterns
        age = features.get("domain_age_days")
        if age is not None and age < 30 and not features.get("ssl_present"):
            return "phishing"

        if features.get("domain_status") == "expired":
            return "suspicious"

        if features.get("proxy_count", 0) > 0 and age is not None and age < 90:
            return "malware_hosting"

        # Score-based classification
        if score <= 20:
            return "legitimate"
        elif score <= 50:
            return "suspicious"
        elif score <= 75:
            return "malware_hosting"
        else:
            return "phishing"

    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate confidence score based on data completeness (0.0-1.0)"""
        checks = [
            features.get("domain_age_days") is not None,
            features.get("whois_available", False),
            features.get("ssl_present") is not None,
            features.get("ssl_score") is not None,
            features.get("total_ips", 0) > 0,
            features.get("dns_a_count", 0) > 0,
            features.get("dns_txt_count", 0) > 0,
        ]

        total_signals = len(checks)
        available_signals = sum(1 for c in checks if c)

        return available_signals / total_signals if total_signals > 0 else 0.0

    def _generate_assessment(self, score, category, features, factors) -> str:
        """Generate natural language threat assessment"""
        cat_labels = {
            "legitimate": "appears to be a legitimate and well-configured domain",
            "suspicious": "shows some suspicious characteristics that warrant caution",
            "malware_hosting": "exhibits patterns consistent with potential malware hosting",
            "phishing": "displays strong indicators of phishing or malicious activity",
        }

        parts = [f"This domain {cat_labels.get(category, 'has unknown risk profile')}."]
        parts.append(f"The overall threat risk score is {score}/100.")

        # Add top contributing factors
        sorted_factors = sorted(factors, key=lambda f: f["points"], reverse=True)
        if sorted_factors:
            top = sorted_factors[:3]
            factor_strs = [f["factor"] for f in top]
            parts.append("Key contributing factors: " + "; ".join(factor_strs) + ".")

        # Domain age context
        age = features.get("domain_age_days")
        if age is not None:
            if age > 3650:
                years = age // 365
                parts.append(
                    f"The domain is well-established at approximately {years} years old, "
                    "which is a positive trust indicator."
                )
            elif age > 365:
                parts.append(f"The domain has been registered for {age} days.")
            elif age < 30:
                parts.append(
                    "WARNING: This is a very recently registered domain. "
                    "New domains are frequently used for malicious purposes."
                )

        # SSL context
        if features.get("ssl_present") and features.get("ssl_score", 0) >= 85:
            parts.append("SSL/TLS configuration is strong and follows modern security standards.")
        elif not features.get("ssl_present"):
            parts.append(
                "WARNING: No SSL/TLS certificate was detected. "
                "All data transmitted to this domain is unencrypted."
            )

        # Infrastructure context
        if features.get("proxy_count", 0) > 0:
            parts.append(
                "Proxy or VPN infrastructure was detected, which may indicate "
                "an attempt to conceal the true hosting location."
            )

        return " ".join(parts)

    def _generate_recommendations(self, score, category, features) -> List[str]:
        """Generate actionable security recommendations"""
        recs = []

        if category == "phishing":
            recs.append("DANGER: This domain shows phishing indicators - exercise extreme caution")
            recs.append("Do NOT enter any personal or financial information on this domain")
            recs.append("Report this domain to your organization's security team")
        elif category == "malware_hosting":
            recs.append("WARNING: This domain may be hosting malicious content")
            recs.append("Avoid downloading any files from this domain")
            recs.append("Run any previously downloaded files through antivirus scanning")
        elif category == "suspicious":
            recs.append("CAUTION: This domain has some suspicious characteristics")
            recs.append("Verify the domain owner independently before trusting it")
            recs.append("Monitor for any unusual activity when interacting with this domain")

        if not features.get("ssl_present"):
            recs.append("No HTTPS detected - do not transmit any sensitive data")

        if not features.get("has_spf"):
            recs.append("No SPF record found - emails claiming to be from this domain could be spoofed")

        if not features.get("has_dmarc"):
            recs.append("No DMARC record found - email authentication is incomplete")

        age = features.get("domain_age_days")
        if age is not None and age < 90:
            recs.append("Very recently registered domain - new domains carry higher risk")

        exp = features.get("days_until_expiration")
        if exp is not None and 0 < exp < 30:
            recs.append("Domain expires soon - verify it is still actively maintained")

        if not recs:
            recs.append("This domain appears well-configured and trustworthy")
            recs.append("Standard security practices are properly implemented")
            recs.append("No significant risk indicators were detected")

        return recs
