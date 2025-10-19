import stripe
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models import User
from app.config import stripe_config

stripe.api_key = stripe_config.SECRET_KEY

def create_or_get_stripe_customer(user: User) -> str:
    """Get existing Stripe customer ID or create new one"""
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": str(user.id)}
    )
    return customer.id

def upgrade_to_pro(db: Session, user: User, is_subscription: bool = False, subscription_id: str = None) -> None:
    """Upgrade user to Pro tier and reset query counter"""
    user.subscription_tier = 'pro'
    user.queries_used_this_month = 0
    user.last_query_reset_date = datetime.utcnow()
    if is_subscription and subscription_id:
        user.stripe_subscription_id = subscription_id
    else:
        user.pro_expires_at = datetime.utcnow() + timedelta(days=30)
    db.commit()

def downgrade_to_free(db: Session, user: User) -> None:
    """Downgrade user to Free tier"""
    user.subscription_tier = 'free'
    user.stripe_subscription_id = None
    user.pro_expires_at = None
    db.commit()

def handle_pro_expiration(db: Session, user: User) -> bool:
    """Check and handle Pro tier expiration for one-time purchases"""
    if user.subscription_tier == 'pro' and user.pro_expires_at:
        if user.pro_expires_at < datetime.utcnow() and not user.stripe_subscription_id:
            downgrade_to_free(db, user)
            return True
    return False
