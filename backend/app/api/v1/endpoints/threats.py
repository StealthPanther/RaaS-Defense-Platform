"""
Threat Intelligence API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import ThreatIntel
from app.models.schemas import ThreatIntelItem
from app.db.session import get_db
from app.services.threat_service import threat_service
from app.services.cache_service import cache
from loguru import logger
from datetime import datetime
from typing import Optional

router = APIRouter()


@router.get("/check/{ip_address}")
async def check_ip_threat(
    ip_address: str,
    db: Session = Depends(get_db)
):
    """
    Check IP address for threat intelligence
    
    Args:
        ip_address: IP address to check
        db: Database session
        
    Returns:
        Threat intelligence data
    """
    # Check cache first
    cache_key = f"threat:{ip_address}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        logger.info(f"Cache hit for IP: {ip_address}")
        return cached_result
    
    # Check database
    db_record = db.query(ThreatIntel).filter(ThreatIntel.ip_address == ip_address).first()
    
    if db_record:
        logger.info(f"Database hit for IP: {ip_address}")
        result = {
            "ip_address": db_record.ip_address,
            "country_code": db_record.country_code,
            "abuse_confidence_score": db_record.abuse_confidence_score,
            "threat_level": threat_service.get_threat_level(db_record.abuse_confidence_score),
            "last_updated": db_record.updated_at.isoformat() if db_record.updated_at else None,
            "source": "database"
        }
        cache.set(cache_key, result, expire=1800)  # 30 min cache
        return result
    
    # Query AbuseIPDB
    try:
        threat_data = await threat_service.check_ip(ip_address)
        
        if not threat_data:
            raise HTTPException(status_code=404, detail="IP address not found or API error")
        
        # Save to database
        threat_intel = ThreatIntel(
            ip_address=threat_data['ip_address'],
            country_code=threat_data.get('country_code'),
            abuse_confidence_score=threat_data['abuse_confidence_score'],
            last_reported_at=datetime.fromisoformat(threat_data['last_reported_at'].replace('Z', '+00:00')) if threat_data.get('last_reported_at') else None
        )
        
        # Check if exists and update, or create new
        existing = db.query(ThreatIntel).filter(ThreatIntel.ip_address == ip_address).first()
        if existing:
            existing.abuse_confidence_score = threat_data['abuse_confidence_score']
            existing.country_code = threat_data.get('country_code')
            existing.last_reported_at = threat_intel.last_reported_at
            existing.updated_at = datetime.utcnow()
        else:
            db.add(threat_intel)
        
        db.commit()
        
        # Prepare response
        result = {
            "ip_address": threat_data['ip_address'],
            "country_code": threat_data.get('country_code'),
            "abuse_confidence_score": threat_data['abuse_confidence_score'],
            "threat_level": threat_service.get_threat_level(threat_data['abuse_confidence_score']),
            "usage_type": threat_data.get('usage_type'),
            "isp": threat_data.get('isp'),
            "total_reports": threat_data.get('total_reports', 0),
            "is_whitelisted": threat_data.get('is_whitelisted', False),
            "source": "abuseipdb"
        }
        
        # Cache the result
        cache.set(cache_key, result, expire=1800)  # 30 min cache
        
        logger.info(f"Checked IP: {ip_address} - Score: {threat_data['abuse_confidence_score']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking IP {ip_address}: {e}")
        raise HTTPException(status_code=500, detail=f"Threat check failed: {str(e)}")


@router.get("/recent")
async def get_recent_threats(
    limit: int = Query(10, ge=1, le=100),
    min_score: int = Query(0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent threat intelligence records
    
    Args:
        limit: Number of records to return
        min_score: Minimum abuse confidence score filter
        db: Database session
        
    Returns:
        List of recent threats
    """
    try:
        query = db.query(ThreatIntel).filter(ThreatIntel.abuse_confidence_score >= min_score)
        threats = query.order_by(ThreatIntel.created_at.desc()).limit(limit).all()
        
        return {
            "total": len(threats),
            "threats": [
                {
                    "ip_address": threat.ip_address,
                    "country_code": threat.country_code,
                    "abuse_confidence_score": threat.abuse_confidence_score,
                    "threat_level": threat_service.get_threat_level(threat.abuse_confidence_score),
                    "created_at": threat.created_at.isoformat()
                }
                for threat in threats
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching recent threats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent threats")
