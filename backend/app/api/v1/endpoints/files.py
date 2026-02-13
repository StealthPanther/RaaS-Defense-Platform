"""
File Upload and Content Scanning API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import math
from collections import Counter
from app.models.schemas import FileUploadResponse
from app.models.database import FileAnalysis
from app.db.session import get_db
from loguru import logger

router = APIRouter()

# Suspicious keywords commonly found in ransomware
SUSPICIOUS_KEYWORDS = [
    'encrypt', 'decrypt', 'ransom', 'bitcoin', 'pay', 'unlock',
    'restore', 'locked', 'crypto', 'wallet', 'deadline', 'files'
]


def calculate_entropy(data: bytes) -> float:
    """
    Calculate Shannon entropy of file data
    Higher entropy suggests encryption
    
    Args:
        data: File bytes
        
    Returns:
        Entropy value (0-8)
    """
    if not data:
        return 0.0
    
    # Count byte frequencies
    byte_counts = Counter(data)
    total_bytes = len(data)
    
    # Calculate entropy
    entropy = 0.0
    for count in byte_counts.values():
        probability = count / total_bytes
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy


def scan_for_keywords(content: str) -> list:
    """
    Scan content for suspicious keywords
    
    Args:
        content: File content as string
        
    Returns:
        List of found keywords
    """
    content_lower = content.lower()
    found = []
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in content_lower:
            found.append(keyword)
    return found


@router.post("/scan", response_model=FileUploadResponse)
async def scan_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Scan uploaded file for ransomware indicators
    
    Args:
        file: Uploaded file
        db: Database session
        
    Returns:
        FileUploadResponse with scan results
    """
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Calculate entropy
        entropy = calculate_entropy(content)
        
        # Determine entropy level
        if entropy >= 7.5:
            entropy_level = "VERY HIGH (Likely Encrypted)"
        elif entropy >= 6.5:
            entropy_level = "HIGH (Possibly Encrypted)"
        elif entropy >= 5.0:
            entropy_level = "MEDIUM (Compressed or Mixed)"
        else:
            entropy_level = "LOW (Normal)"
        
        # Scan for keywords (decode as text if possible)
        found_keywords = []
        try:
            text_content = content.decode('utf-8', errors='ignore')
            found_keywords = scan_for_keywords(text_content)
        except:
            logger.warning(f"Could not decode file {file.filename} as text")
        
        # Determine verdict
        if entropy >= 7.5 or len(found_keywords) >= 3:
            verdict = "SUSPICIOUS"
        elif entropy >= 6.5 or len(found_keywords) >= 2:
            verdict = "CAUTION"
        else:
            verdict = "CLEAN"
        
        # Save to database
        analysis = FileAnalysis(
            filename=file.filename,
            file_size=file_size,
            entropy_score=entropy,
            entropy_level=entropy_level,
            suspicious_keywords=','.join(found_keywords),
            verdict=verdict
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Scanned file: {file.filename} - Verdict: {verdict}")
        
        return FileUploadResponse(
            filename=file.filename,
            filesize=file_size,
            entropy_score=f"{entropy:.2f}",
            entropy_level=entropy_level,
            found_keywords=found_keywords,
            verdict=verdict
        )
        
    except Exception as e:
        logger.error(f"Error scanning file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"File scan failed: {str(e)}")
