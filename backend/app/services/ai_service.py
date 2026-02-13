"""
AI Service for Gemini Chatbot Integration
"""
import google.generativeai as genai
from app.config import settings
from loguru import logger
from typing import Optional


class AIService:
    """Google Gemini AI service for ransomware assistance chatbot"""
    
    def __init__(self):
        """Initialize Gemini AI"""
        self.model = None
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini model"""
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True
            logger.info("✅ Gemini AI initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.initialized = False
    
    def get_response(self, message: str, context: Optional[str] = None) -> str:
        """
        Get AI response for user message
        
        Args:
            message: User message
            context: Optional context (e.g., previous conversation)
            
        Returns:
            AI response string
        """
        if not self.initialized or not self.model:
            return "AI service is currently unavailable. Please try again later."
        
        try:
            # System prompt for ransomware defense context
            system_context = """You are an expert cybersecurity assistant specializing in ransomware defense. 
            You help users understand ransomware threats, identify suspicious files, and provide recovery guidance.
            Keep responses concise, practical, and security-focused. If asked about payment, always advise against 
            paying ransoms and suggest proper incident response procedures."""
            
            # Construct prompt
            prompt = f"{system_context}\n\nUser Question: {message}\n\nAssistant:"
            
            if context:
                prompt = f"{system_context}\n\nContext: {context}\n\nUser Question: {message}\n\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return "I couldn't generate a response. Please rephrase your question."
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "An error occurred while processing your request. Please try again."


# Global AI service instance
ai_service = AIService()
