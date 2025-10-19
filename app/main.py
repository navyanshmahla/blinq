from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import sys
import os
import time
from uuid import uuid4
from dotenv import load_dotenv

sys.path.append("../")

from app.logger import app_logger
from app.metrics import http_requests_total, http_request_duration_seconds


app = FastAPI(
    title="Blinq API",
    version="1.0.0",
    docs_url = None if os.getenv("ENVIRONMENT")=="prod" else "/docs")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

if os.getenv("ENVIRONMENT") == "production":
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "").split(",")
    if trusted_hosts and trusted_hosts[0]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

@app.middleware("http")
async def log_and_measure_requests(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    app_logger.info(
        "Request started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    response = await call_next(request)
    duration = time.time() - start_time

    app_logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": int(duration * 1000),
            "request_id": request_id
        }
    )

    http_requests_total.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)

    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

from app.routers import auth, plots, data, analysis, conversations, credits, payments

app.include_router(auth.router, prefix="/api/auth")
app.include_router(conversations.router, prefix="/api/conversations")
app.include_router(plots.router, prefix="/api/plots")
app.include_router(data.router, prefix="/api/data")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(credits.router, prefix="/api/credits")
app.include_router(payments.router, prefix="/api/payments")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "blinq"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
