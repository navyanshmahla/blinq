from pydantic import BaseModel

class SubscriptionLimits(BaseModel):
    """Query limits per subscription tier"""
    FREE_QUERIES_PER_MONTH: int = 5
    PRO_QUERIES_PER_MONTH: int = 100
    BONUS_CREDIT_PACK_SIZE: int = 10

subscription_limits = SubscriptionLimits()
