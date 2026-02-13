"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class FilenameAnalyzeRequest(BaseModel):
    """Request schema for filename analysis"""
    filename: str = Field(..., min_length=1, max_length=255, description="Filename to analyze")
    
    @validator('filename')
    def filename_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Filename cannot be empty')
        return v


class FilenameAnalyzeResponse(BaseModel):
    """Response schema for filename analysis"""
    score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    level: str = Field(..., description="Risk level assessment")
    reasons: list[str] = Field(default_factory=list, description="Reasons for assessment")
    advice: str = Field(..., description="Recommended action")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")


class ChatRequest(BaseModel):
    """Request schema for chatbot"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")


class ChatResponse(BaseModel):
    """Response schema for chatbot"""
    reply: str = Field(..., description="AI response")


class FileUploadResponse(BaseModel):
    """Response schema for file upload analysis"""
    filename: str
    filesize: int
    entropy_score: str
    entropy_level: str
    found_keywords: list[str]
    verdict: str


class ScanHistory(BaseModel):
    """Schema for scan history records"""
    id: int
    filename: str
    score: int
    level: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ThreatIntelItem(BaseModel):
    """Schema for threat intelligence item"""
    ip_address: str
    country_code: Optional[str] = None
    abuse_confidence_score: int
    
    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    environment: str
    database: str = "connected"
    redis: str = "connected"
