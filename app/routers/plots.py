from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db, crud

router = APIRouter(tags=["plots"])

@router.get("/{request_id}")
async def get_plot(request_id: UUID, db: Session = Depends(get_db)):
    """Fallback endpoint to poll for plot if it wasn't ready in analysis response"""
    plot = crud.get_plot_by_request_id(db, request_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not ready yet")
    return Response(content=plot.image_data, media_type="image/png")
