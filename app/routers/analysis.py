from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import polars as pl
import io
import sys
import os
import asyncio
import base64
from uuid import UUID
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from agent.agents.main_agent import run_main_agent
from app.db import get_db, crud, schemas
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["analysis"])

async def wait_for_plot_in_db(db: Session, request_id: str, timeout: int = 60):
    """Poll database for plot with exponential backoff"""
    end_time = datetime.utcnow() + timedelta(seconds=timeout)
    wait_interval = 0.1

    while datetime.utcnow() < end_time:
        plot = crud.get_plot_by_request_id(db, UUID(request_id))
        if plot:
            return plot.image_data

        await asyncio.sleep(wait_interval)
        wait_interval = min(wait_interval * 1.5, 2)
        db.expire_all()

    return None

@router.post("/")
async def call_agent_api(
    conversation_id: UUID = Form(...),
    file: UploadFile = File(None),
    query: str = Form(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run data analysis on uploaded CSV file within a conversation"""
    try:
        conversation = crud.get_conversation_by_id(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if str(conversation.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if not conversation.csv_id:
            if not file:
                raise HTTPException(status_code=400, detail="No CSV linked. Please upload a CSV first.")
            raise HTTPException(status_code=400, detail="Please use /conversations/{id}/upload-csv endpoint first")

        if conversation.csv_expires_at and conversation.csv_expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="CSV expired. Please re-upload via /conversations/{id}/upload-csv")

        csv_file = crud.get_csv_by_id(db, conversation.csv_id)
        if not csv_file:
            raise HTTPException(status_code=404, detail="CSV file not found")

        df = pl.read_csv(io.BytesIO(csv_file.csv_data))

        user_message = crud.create_message(db, schemas.MessageCreate(
            conversation_id=conversation_id,
            role='user',
            content=query
        ))

        result, total_cost, is_plotting, request_id = await run_main_agent(df, input=query)

        assistant_message = crud.create_message(db, schemas.MessageCreate(
            conversation_id=conversation_id,
            role='assistant',
            content=result,
            cost=total_cost,
            request_id=request_id,
            is_plotting=is_plotting
        ))

        crud.extend_csv_expiration(db, conversation_id)

        crud.create_usage_tracking(db, schemas.UsageTrackingCreate(
            user_id=UUID(user_id),
            message_id=assistant_message.id,
            cost=total_cost,
            model_used="grok-4-reasoning-fast"
        ))

        response_data = {
            "response": result,
            "is_plotting": is_plotting,
            "cost": total_cost,
            "request_id": request_id,
            "message_id": str(assistant_message.id),
            "status": "success"
        }

        if is_plotting and request_id:
            plot_data = await wait_for_plot_in_db(db, request_id, timeout=60)
            if plot_data:
                plot = crud.get_plot_by_request_id(db, UUID(request_id))
                plot.message_id = assistant_message.id
                db.commit()
                response_data["plot_image"] = base64.b64encode(plot_data).decode('utf-8')
                response_data["plot_status"] = "ready"
            else:
                response_data["plot_status"] = "processing"

        return JSONResponse(content=response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
