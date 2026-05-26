from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.chat import ChatHistory
from app.schemas.chat import SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{user_id}")
async def get_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ChatHistory.session_id).filter(
        ChatHistory.user_id == user_id
    ).distinct().all()

    return [s[0] for s in sessions]


# ============================================================================
# Session & History Endpoints
# ============================================================================

# @router.get("/sessions/{user_id}", response_model=list[SessionResponse])
# async def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
#     """
#     Get all chat sessions for a user with recent messages.
#     """
#     try:
#         # Get distinct sessions with their latest message
#         sessions = db.query(
#             ChatHistory.session_id,
#             ChatHistory.created_at
#         ).filter(
#             ChatHistory.user_id == user_id
#         ).order_by(
#             ChatHistory.created_at.desc()
#         ).distinct(ChatHistory.session_id).all()
        
#         result = []
#         for session_id, _ in sessions:
#             # Get messages for this session
#             messages = db.query(ChatHistory).filter(
#                 ChatHistory.user_id == user_id,
#                 ChatHistory.session_id == session_id
#             ).order_by(ChatHistory.created_at.asc()).all()
            
#             if messages:
#                 result.append(SessionResponse(
#                     session_id=session_id,
#                     last_message=messages[-1].content,
#                     last_updated=messages[-1].created_at,
#                     message_count=len(messages)
#                 ))
        
#         return result
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=list[SessionResponse])
async def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    try:
        # 1. Fix the DISTINCT ON error by adding session_id to order_by
        # 2. Optimized: We don't need to query for ALL messages just to get counts/last messages
        #    if you have a 'sessions' table. 
        #    Assuming you only have 'chat_history', this approach is much faster:
        
        # Get the latest record for each session_id
        latest_records = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).distinct(ChatHistory.session_id).order_by(
            ChatHistory.session_id,           # Must come first for DISTINCT ON
            ChatHistory.created_at.desc()     # Get the latest message
        ).all()
        
        # Get counts in a separate simple query (or via a subquery if you prefer)
        # This is much faster than fetching all full message objects
        result = []
        for record in latest_records:
            count = db.query(ChatHistory).filter(
                ChatHistory.session_id == record.session_id
            ).count()
            
            result.append(SessionResponse(
                id=record.session_id,
                message_count=count,
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/{user_id}/{session_id}/messages")
async def get_session_messages(user_id: int, session_id: str, db: Session = Depends(get_db)):
    """
    Get all messages for a specific session.
    """
    try:
        messages = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.created_at.asc()).all()
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
                "command_id": msg.command_id,
                "report_id": msg.report_id,
                "image_id": msg.image_id
            }
            for msg in messages
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


