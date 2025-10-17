from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import polars as pl
import io
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from agent.agents.main_agent import run_main_agent

router = APIRouter(tags=["analysis"])

@router.post("/")
async def call_agent_api(
    file: UploadFile = File(...),
    query: str = Form(...)
):
    """Run data analysis on uploaded CSV file"""
    try:
        csv_bytes = await file.read()
        df = pl.read_csv(io.BytesIO(csv_bytes))

        result, total_cost, is_plotting, request_id = await run_main_agent(df, input=query)

        return JSONResponse(content={
            "response": result,
            "is_plotting": is_plotting,
            "cost": total_cost,
            "request_id": request_id,
            "status": "success"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
