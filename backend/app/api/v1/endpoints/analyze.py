"""
Filename Analysis API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import FilenameAnalyzeRequest, FilenameAnalyzeResponse
from app.models.database import Scan
from app.db.session import get_db
from app.services.ml_service import ml_service
from app.services.cache_service import cache
from loguru import logger

router = APIRouter()


@router.post("/analyze", response_model=FilenameAnalyzeResponse)
async def analyze_filename(
    request: FilenameAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a filename for ransomware indicators
    
    Args:
        request: FilenameAnalyzeRequest with filename
        db: Database session
        
    Returns:
        FilenameAnalyzeResponse with analysis results
    """
    filename = request.filename
    
    # Check cache first
    cache_key = f"analyze:{filename}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        logger.info(f"Cache hit for filename: {filename}")
        return FilenameAnalyzeResponse(**cached_result)
    
    # Analyze filename
    try:
        result = ml_service.analyze_filename(filename)
        
        # Save to database
        scan = Scan(
            filename=filename,
            score=result['score'],
            level=result['level'],
            confidence=result['confidence'],
            is_malicious=result['score'] >= 40
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        
        # Cache the result (1 hour TTL)
        result_data = {
            "score": result['score'],
            "level": result['level'],
            "reasons": result['reasons'],
            "advice": result['advice'],
            "confidence": result['confidence']
        }
        cache.set(cache_key, result_data, expire=3600)
        
        logger.info(f"Analyzed filename: {filename} - Score: {result['score']}")
        
        return FilenameAnalyzeResponse(**result_data)
        
    except Exception as e:
        logger.error(f"Error analyzing filename {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/history")
async def get_scan_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent scan history
    
    Args:
        limit: Number of records to return
        db: Database session
        
    Returns:
        List of recent scans
    """
    try:
        scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(limit).all()
        return {
            "total": len(scans),
            "scans": [
                {
                    "id": scan.id,
                    "filename": scan.filename,
                    "score": scan.score,
                    "level": scan.level,
                    "confidence": scan.confidence,
                    "created_at": scan.created_at.isoformat()
                }
                for scan in scans
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching scan history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")
