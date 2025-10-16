from fastapi import APIRouter

router = APIRouter(tags=["plots"])

@router.get("/")
async def get_plots():
    """Get all plots"""
    return {"message": "Plots endpoint - implement as needed"}

@router.post("/")
async def create_plot():
    """Create new plot"""
    return {"message": "Create plot endpoint - implement as needed"}
