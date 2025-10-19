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

class RazorpayConfig(BaseModel):
    """Razorpay configuration"""
    KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

subscription_limits = SubscriptionLimits()
pricing = Pricing()
razorpay_config = RazorpayConfig()
