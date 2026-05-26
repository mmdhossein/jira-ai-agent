from tkinter import Image

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.n8n_client import N8NClient
from app.models.chat import ChatHistory
from app.models.command import Command
from app.models.report import Report
import json 

router = APIRouter(prefix="/chat", tags=["chat"])

# ============================================================================
# Chat Endpoints
# ============================================================================

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint. Processes user message and returns AI response.
    Flow: User Input → n8n (intent classification) → Jira API → n8n (report generation) → Response
    """
    try:
        messages = db.query(ChatHistory).filter(
            ChatHistory.user_id == request.user_id,
            ChatHistory.session_id == request.session_id
        ).order_by(ChatHistory.created_at.asc()).all()
        
        previous_messages = [
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
        previous_messages = json.dumps(previous_messages, default=str)  # Convert datetime to string for JSON serialization
        # Save user message to chat history
        user_message = ChatHistory(
            user_id=request.user_id,
            session_id=request.session_id,
            role="user",
            content=request.message,
        )
        db.add(user_message)
        db.commit()

        if request.project_name is None: # todo
            request.project_name = 'all'
        
        # Send to n8n for processing
        n8n_client = N8NClient()
        n8n_response = await n8n_client.process_chat(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id,
            current_project=request.project_name,
            chat_history=previous_messages)
            # todo pass the page context! 
        print("RESPONSE: ", json.dumps(n8n_response))
        
        if not n8n_response.get("success"):
            {"success": False, "message": "I encountered an error while trying to retrieve the requested Jira information (Error: ERR_BAD_REQUEST). Please verify your request or try again later.", "report": {}}
            return ChatResponse(
            success=False,
            message=n8n_response.get("message", ""),
            action='',
            report_id=None,
            command_id=None,
            # generate_image=generate_image, # flags for front to decide the file generation
            # generate_pdf=generate_pdf, # flags for front to decide the file generation
            data={},
            flags={}
        )
            raise HTTPException(status_code=500, detail=n8n_response.get("error", "Processing failed"))
        
        # Extract response data
        action = n8n_response.get("action", "chat")
        # data = n8n_response.get("data", {})
        data = n8n_response
        assistant_message = data.get("message", "I've processed your request.")
        # Save command if action is identified
        command_id = None
        if action and action == 'command' : # todo be clear if user intended to receives weekly report or not this way he is responsible for multiple same commands for now
            command = Command(
                user_id=request.user_id,
                session_id=request.session_id,
                query=request.message,
                action=action
            )
            db.add(command)
            db.commit()
            db.refresh(command)
            command_id = command.id
            print("Saved the command")
        # Save report if generated
        report_id = None
        if data.get("report"):
            assistant_message += '\n\n' + data["report"].get("summary") 
            report = Report(
                command_id=command_id,
                report_type=action or "general",
                summary=data["report"].get("summary"),
                chart_data=data["report"].get("chart_data"),
                structured_data=data["report"].get("structured_data")
                ,project_name=request.project_name
                
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            report_id = report.id
        
        # Save image if generated
        # image_id = None
        # if data.get("image_data"):
        #     image = Image(
        #         report_id=report_id,
        #         image_data=data["image_data"],
        #         image_type=data.get("image_type", "png")
        #     )
        #     db.add(image)
        #     db.commit()
        #     db.refresh(image)
        #     image_id = image.id
        
        # Save assistant message to chat history
        assistant_chat = ChatHistory(
            user_id=request.user_id,
            session_id=request.session_id,
            role="assistant",
            content=assistant_message,
            command_id=command_id,
            report_id=report_id,
            image_id=None, 
        )
        db.add(assistant_chat)
        db.commit()
        
        return ChatResponse(
            success=True,
            message=assistant_message,
            action=action,
            report_id=report_id,
            command_id=command_id,
            # generate_image=generate_image, # flags for front to decide the file generation
            # generate_pdf=generate_pdf, # flags for front to decide the file generation
            data=data,
            flags=data.get("flags", {})
        )
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

