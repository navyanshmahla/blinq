from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append("../")

app = FastAPI(title="Blinq API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import plots, data, analysis
from app.websockets.plots import router as ws_plots_router
from app.background.kafka_consumers import start_consumers, stop_consumers

app.include_router(plots.router, prefix="/api/plots")
app.include_router(data.router, prefix="/api/data")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(ws_plots_router, prefix="/ws")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "blinq"}

@app.on_event("startup")
async def startup():
    """Start background tasks"""
    await start_consumers()

@app.on_event("shutdown")
async def shutdown():
    """Graceful shutdown"""
    await stop_consumers()
