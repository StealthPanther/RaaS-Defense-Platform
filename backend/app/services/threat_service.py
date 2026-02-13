"""
Threat Intelligence Service using AbuseIPDB
"""
import httpx
from typing import Optional, Dict
from app.config import settings
from loguru import logger
from datetime import datetime


class ThreatService:
    """AbuseIPDB threat intelligence service"""
    
    def __init__(self):
        """Initialize threat service"""
        self.api_key = settings.ABUSEIPDB_API_KEY
        self.base_url = "https://api.abuseipdb.com/api/v2"
        self.headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }
    
    async def check_ip(self, ip_address: str) -> Optional[Dict]:
        """
        Check IP address against AbuseIPDB
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Dict with threat intelligence data or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/check",
                    headers=self.headers,
                    params={
                        "ipAddress": ip_address,
                        "maxAgeInDays": 90
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", {})
                    
                    return {
                        "ip_address": result.get("ipAddress"),
                        "country_code": result.get("countryCode"),
                        "abuse_confidence_score": result.get("abuseConfidenceScore", 0),
                        "usage_type": result.get("usageType"),
                        "isp": result.get("isp"),
                        "domain": result.get("domain"),
                        "is_whitelisted": result.get("isWhitelisted", False),
                        "total_reports": result.get("totalReports", 0),
                        "last_reported_at": result.get("lastReportedAt")
                    }
                else:
                    logger.warning(f"AbuseIPDB API returned status {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout checking IP {ip_address}")
            return None
        except Exception as e:
            logger.error(f"Error checking IP {ip_address}: {e}")
            return None
    
    def get_threat_level(self, abuse_score: int) -> str:
        """
        Determine threat level based on abuse confidence score
        
        Args:
            abuse_score: Abuse confidence score (0-100)
            
        Returns:
            Threat level string
        """
        if abuse_score >= 75:
            return "CRITICAL"
        elif abuse_score >= 50:
            return "HIGH"
        elif abuse_score >= 25:
            return "MEDIUM"
        elif abuse_score > 0:
            return "LOW"
        else:
            return "CLEAN"


# Global threat service instance
threat_service = ThreatService()
