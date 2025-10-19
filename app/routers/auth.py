from fastapi import APIRouter, Depends, HTTPException, status, Form, Response, Request
from sqlalchemy.orm import Session
from app.db import get_db, crud, schemas
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, get_current_user
from uuid import UUID
import os
import time

from app.logger import app_logger
from app.metrics import (
    login_attempts_total,
    signup_attempts_total,
    token_refresh_total
)

router = APIRouter(tags=["authentication"])
limiter = None

def get_limiter():
    from app.main import limiter as app_limiter
    global limiter
    if limiter is None:
        limiter = app_limiter
    return limiter

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    get_limiter().limit("3/minute")(lambda: None)()

    app_logger.info(
        "Signup attempt",
        extra={
            "email": email,
            "ip": request.client.host if request.client else "unknown",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

    try:
        existing_user = crud.get_user_by_email(db, email)
        if existing_user:
            app_logger.warning(
                "Signup failed - email already exists",
                extra={"email": email}
            )
            signup_attempts_total.labels(status="failed").inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user_data = schemas.UserCreate(email=email, password=password, full_name=full_name)
        password_hash = hash_password(password)
        user = crud.create_user(db, user_data, password_hash)

        app_logger.info(
            "Signup successful",
            extra={
                "user_id": str(user.id),
                "email": email
            }
        )
        signup_attempts_total.labels(status="success").inc()

        return user

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(
            "Signup error",
            extra={"email": email, "error": str(e)},
            exc_info=True
        )
        signup_attempts_total.labels(status="error").inc()
        raise

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    get_limiter().limit("5/minute")(lambda: None)()
    start_time = time.time()

    app_logger.info(
        "Login attempt",
        extra={
            "email": email,
            "ip": request.client.host if request.client else "unknown",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

    try:
        user = crud.get_user_by_email(db, email)
        if not user:
            app_logger.warning(
                "Login failed - user not found",
                extra={"email": email}
            )
            login_attempts_total.labels(status="failed").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not verify_password(password, user.password_hash):
            app_logger.warning(
                "Login failed - incorrect password",
                extra={"email": email, "user_id": str(user.id)}
            )
            login_attempts_total.labels(status="failed").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_str, expires_at = create_refresh_token(data={"sub": str(user.id)})
        crud.create_refresh_token(db, schemas.RefreshTokenCreate(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=expires_at
        ))

        is_secure = os.getenv("ENVIRONMENT") == "production"

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=is_secure,
            samesite="lax",
            max_age=900
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token_str,
            httponly=True,
            secure=is_secure,
            samesite="strict",
            max_age=2592000
        )

        duration = time.time() - start_time
        app_logger.info(
            "Login successful",
            extra={
                "user_id": str(user.id),
                "email": email,
                "duration_ms": int(duration * 1000)
            }
        )
        login_attempts_total.labels(status="success").inc()

        return {
            "user_id": str(user.id),
            "email": user.email,
            "subscription_tier": user.subscription_tier
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(
            "Login error",
            extra={"email": email, "error": str(e)},
            exc_info=True
        )
        login_attempts_total.labels(status="error").inc()
        raise

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    get_limiter().limit("10/minute")(lambda: None)()

    app_logger.debug(
        "Token refresh attempt",
        extra={"request_id": getattr(request.state, "request_id", None)}
    )

    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            app_logger.warning("Token refresh failed - no token provided")
            token_refresh_total.labels(status="failed").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token provided"
            )

        user_id = verify_token(refresh_token, token_type="refresh")
        if not user_id:
            app_logger.warning("Token refresh failed - invalid token")
            token_refresh_total.labels(status="failed").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        db_token = crud.get_refresh_token_by_token(db, refresh_token)
        if not db_token or db_token.is_revoked:
            app_logger.warning(
                "Token refresh failed - token revoked",
                extra={"user_id": user_id}
            )
            token_refresh_total.labels(status="failed").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked or invalid"
            )

        new_access_token = create_access_token(data={"sub": user_id})

        is_secure = os.getenv("ENVIRONMENT") == "production"
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=is_secure,
            samesite="lax",
            max_age=900
        )

        app_logger.info(
            "Token refreshed successfully",
            extra={"user_id": user_id}
        )
        token_refresh_total.labels(status="success").inc()

        return {"message": "Token refreshed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(
            "Token refresh error",
            extra={"error": str(e)},
            exc_info=True
        )
        token_refresh_total.labels(status="error").inc()
        raise

@router.post("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        crud.revoke_refresh_token(db, refresh_token)
        app_logger.info("User logged out")

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Logged out successfully"}

@router.post("/logout-all")
async def logout_all(response: Response, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    count = crud.revoke_all_user_tokens(db, UUID(user_id))

    app_logger.info(
        "User logged out from all devices",
        extra={"user_id": user_id, "tokens_revoked": count}
    )

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": f"Revoked {count} tokens"}
