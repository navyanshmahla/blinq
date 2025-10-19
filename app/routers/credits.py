from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db, crud
from app.auth import get_current_user
from app.utils.quota import add_bonus_credits, get_remaining_queries
from app.config import subscription_limits
from uuid import UUID

router = APIRouter(tags=["credits"])

@router.post("/purchase")
async def purchase_credits(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase bonus credit pack (say N queries)"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    add_bonus_credits(db, user)
    return {
        "message": f"Successfully added {subscription_limits.BONUS_CREDIT_PACK_SIZE} bonus credits",
        "bonus_credits": user.bonus_credits
    }

@router.get("/balance")
async def get_credit_balance(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current query balance"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return get_remaining_queries(user)
