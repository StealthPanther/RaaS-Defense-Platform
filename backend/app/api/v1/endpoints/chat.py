"""
AI Chatbot API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse
from app.models.database import ChatMessage
from app.db.session import get_db
from app.services.ai_service import ai_service
from loguru import logger

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant about ransomware defense
    
    Args:
        request: ChatRequest with user message
        db: Database session
        
    Returns:
        ChatResponse with AI reply
    """
    try:
        message = request.message
        
        # Get AI response
        reply = ai_service.get_response(message)
        
        # Save to database
        chat_msg = ChatMessage(
            message=message,
            response=reply
        )
        db.add(chat_msg)
        db.commit()
        db.refresh(chat_msg)
        
        logger.info(f"Chat message processed: {message[:50]}...")
        
        return ChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/history")
async def get_chat_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent chat history
    
    Args:
        limit: Number of messages to return
        db: Database session
        
    Returns:
        List of recent chat messages
    """
    try:
        messages = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        return {
            "total": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "message": msg.message,
                    "response": msg.response,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")
