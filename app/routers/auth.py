from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from sqlalchemy.orm import Session
from app.db import get_db, crud, schemas
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, get_current_user
from uuid import UUID

router = APIRouter(tags=["authentication"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_data = schemas.UserCreate(email=email, password=password, full_name=full_name)
    password_hash = hash_password(password)
    user = crud.create_user(db, user_data, password_hash)

    return user

@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not verify_password(password, user.password_hash):
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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
        "subscription_tier": user.subscription_tier
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user_id = verify_token(refresh_token, token_type="refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    db_token = crud.get_refresh_token_by_token(db, refresh_token)
    if not db_token or db_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked or invalid"
        )
    new_access_token = create_access_token(data={"sub": user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    revoked = crud.revoke_refresh_token(db, refresh_token)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    return {"message": "Logged out successfully"}

@router.post("/logout-all")
async def logout_all(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    count = crud.revoke_all_user_tokens(db, UUID(user_id))
    return {"message": f"Revoked {count} tokens"}
