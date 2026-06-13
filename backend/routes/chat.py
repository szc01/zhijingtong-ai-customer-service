from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from backend import models, schemas
from backend.database import get_db
from backend.dependencies import get_current_active_user
from agent.react_agent import ReactAgent

router = APIRouter()

agent = ReactAgent()


@router.post("/", response_model=schemas.ChatResponse)
async def chat(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    try:
        response_chunks = []
        for chunk in agent.execute_stream(request.message):
            response_chunks.append(chunk)
        
        response_text = "".join(response_chunks)
        
        chat_history = models.ChatHistory(
            user_id=current_user.id,
            user_message=request.message,
            agent_response=response_text
        )
        db.add(chat_history)
        db.commit()
        
        return schemas.ChatResponse(
            message=request.message,
            response=response_text,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")


@router.post("/stream")
async def chat_stream(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_active_user)
):
    async def generate():
        for chunk in agent.execute_stream(request.message):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/history")
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.created_at.desc()).all()
    
    return [{
        "id": h.id,
        "user_message": h.user_message,
        "agent_response": h.agent_response,
        "created_at": h.created_at
    } for h in history]