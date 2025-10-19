from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
import polars as pl
import io

from app.db import get_db, crud, schemas
from app.db.models import Conversation, CSVFile
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["conversations"])

@router.post("/", response_model=schemas.ConversationResponse)
async def create_conversation(
    title: str = Form("New Chat"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.create_conversation(db, user_id=UUID(user_id), title=title)
    return conversation

@router.get("/", response_model=List[schemas.ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversations = crud.get_user_conversations(db, user_id=UUID(user_id), skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=schemas.ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conversation.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return conversation

@router.patch("/{conversation_id}", response_model=schemas.ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    title: str = Form(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conversation.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = crud.update_conversation_title(db, conversation_id, title)
    return updated

@router.get("/{conversation_id}/messages", response_model=List[schemas.MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conversation.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    messages = crud.get_conversation_messages(db, conversation_id, skip=skip, limit=limit)
    return messages

@router.post("/{conversation_id}/upload-csv", response_model=schemas.CSVFileResponse)
async def upload_csv(
    conversation_id: UUID,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conversation.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    csv_bytes = await file.read()
    df = pl.read_csv(io.BytesIO(csv_bytes))

    csv_data = schemas.CSVFileCreate(
        conversation_id=conversation_id,
        filename=file.filename,
        file_size=len(csv_bytes),
        row_count=df.shape[0],
        column_names=df.columns,
        csv_data=csv_bytes,
        expires_at=datetime.utcnow() + timedelta(weeks=1)
    )

    csv_file = crud.create_csv_file(db, user_id=UUID(user_id), csv_data=csv_data)

    crud.link_csv_to_conversation(
        db,
        conversation_id=conversation_id,
        csv_id=csv_file.id,
        expires_at=csv_file.expires_at
    )

    return csv_file

@router.get("/{conversation_id}/csv", response_model=schemas.CSVFileResponse)
async def get_conversation_csv(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conversation.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if not conversation.csv_id:
        raise HTTPException(status_code=404, detail="No CSV linked to this conversation")

    csv_file = crud.get_csv_by_id(db, conversation.csv_id)
    if not csv_file:
        raise HTTPException(status_code=404, detail="CSV file not found")

    return csv_file
