from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models import User
from app.config import subscription_limits

def get_query_limit(subscription_tier: str) -> int:
    """Get monthly query limit for subscription tier"""
    if subscription_tier == 'free':
        return subscription_limits.FREE_QUERIES_PER_MONTH
    elif subscription_tier == 'pro':
        return subscription_limits.PRO_QUERIES_PER_MONTH
    return 0

def check_query_quota(user: User) -> bool:
    """Check if user has available queries"""
    monthly_limit = get_query_limit(user.subscription_tier)
    if user.queries_used_this_month < monthly_limit:
        return True
    if user.bonus_credits > 0:
        return True
    return False

def decrement_query_usage(db: Session, user: User) -> None:
    """Deduct query from user's quota (monthly first, then bonus)"""
    monthly_limit = get_query_limit(user.subscription_tier)
    if user.queries_used_this_month < monthly_limit:
        user.queries_used_this_month += 1
    elif user.bonus_credits > 0:
        user.bonus_credits -= 1
    db.commit()

def reset_monthly_quota(db: Session, user: User) -> None:
    """Reset monthly query counter if needed"""
    days_since_reset = (datetime.utcnow() - user.last_query_reset_date).days
    if days_since_reset >= 30:
        user.queries_used_this_month = 0
        user.last_query_reset_date = datetime.utcnow()
        db.commit()

def add_bonus_credits(db: Session, user: User, amount: int = None) -> None:
    """Add bonus credits to user account"""
    if amount is None:
        amount = subscription_limits.BONUS_CREDIT_PACK_SIZE
    user.bonus_credits += amount
    db.commit()

def get_remaining_queries(user: User) -> dict:
    """Get breakdown of remaining queries"""
    monthly_limit = get_query_limit(user.subscription_tier)
    monthly_remaining = max(0, monthly_limit - user.queries_used_this_month)
    return {
        "monthly_remaining": monthly_remaining,
        "bonus_credits": user.bonus_credits,
        "total_available": monthly_remaining + user.bonus_credits
    }
