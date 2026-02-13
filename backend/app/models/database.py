"""
SQLAlchemy Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Scan(Base):
    """Filename scan results"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    level = Column(String(50), nullable=False)
    confidence = Column(Float)
    is_malicious = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Scan {self.filename} - Score: {self.score}>"


class ChatMessage(Base):
    """AI Chatbot conversation history"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ChatMessage {self.id}>"


class ThreatIntel(Base):
    """Cached threat intelligence data"""
    __tablename__ = "threat_intel"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True)  # IPv6 support
    country_code = Column(String(2))
    abuse_confidence_score = Column(Integer)
    last_reported_at = Column(DateTime)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ThreatIntel {self.ip_address}>"


class FileAnalysis(Base):
    """File content analysis results"""
    __tablename__ = "file_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    entropy_score = Column(Float)
    entropy_level = Column(String(50))
    suspicious_keywords = Column(Text)  # JSON string
    verdict = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<FileAnalysis {self.filename}>"
