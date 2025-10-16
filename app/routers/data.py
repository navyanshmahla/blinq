from fastapi import APIRouter

router = APIRouter(tags=["data"])

@router.post("/upload")
async def upload_data():
    """Upload CSV data"""
    return {"message": "Data upload endpoint - implement as needed"}

@router.get("/query")
async def query_data():
    """Query data"""
    return {"message": "Data query endpoint - implement as needed"}
