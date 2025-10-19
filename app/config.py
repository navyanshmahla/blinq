from pydantic import BaseModel
import os

class SubscriptionLimits(BaseModel):
    """Query limits per subscription tier"""
    FREE_QUERIES_PER_MONTH: int = 5
    PRO_QUERIES_PER_MONTH: int = 100
    BONUS_CREDIT_PACK_SIZE: int = 10

class Pricing(BaseModel):
    """Pricing in cents (USD)"""
    PRO_MONTHLY_SUBSCRIPTION: int = 1000
    PRO_ONETIME_30_DAYS: int = 1200
    BONUS_CREDIT_PACK: int = 500

class StripeConfig(BaseModel):
    """Stripe configuration"""
    SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    PRO_PRICE_ID: str = os.getenv("STRIPE_PRO_PRICE_ID", "")

subscription_limits = SubscriptionLimits()
pricing = Pricing()
stripe_config = StripeConfig()
