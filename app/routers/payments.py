from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
import razorpay
import hmac
import hashlib
from uuid import UUID
from app.db import get_db, crud
from app.db.models import User
from app.auth import get_current_user
from app.config import razorpay_config, pricing
from app.utils.razorpay_helpers import create_or_get_razorpay_customer, upgrade_to_pro, downgrade_to_free
from app.utils.quota import add_bonus_credits

router = APIRouter(tags=["payments"])
client = razorpay.Client(auth=(razorpay_config.KEY_ID, razorpay_config.KEY_SECRET))

@router.post("/create-subscription")
async def create_pro_subscription(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay subscription for Pro plan"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    razorpay_customer_id = create_or_get_razorpay_customer(user)
    if not user.razorpay_customer_id:
        user.razorpay_customer_id = razorpay_customer_id
        db.commit()

    plan = client.plan.create(data={
        "period": "monthly",
        "interval": 1,
        "item": {
            "name": "Pro Plan - Monthly",
            "amount": pricing.PRO_MONTHLY_SUBSCRIPTION,
            "currency": "USD"
        }
    })

    subscription = client.subscription.create(data={
        "plan_id": plan['id'],
        "customer_id": razorpay_customer_id,
        "total_count": 12,
        "notify_info": {
            "notify_email": user.email
        },
        "notes": {
            "user_id": str(user.id),
            "type": "pro_subscription"
        }
    })

    return {
        "subscription_id": subscription['id'],
        "razorpay_key": razorpay_config.KEY_ID,
        "amount": pricing.PRO_MONTHLY_SUBSCRIPTION,
        "currency": "USD"
    }

@router.post("/create-order/pro-onetime")
async def create_pro_onetime_order(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay order for one-time Pro purchase (30 days)"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order = client.order.create(data={
        "amount": pricing.PRO_ONETIME_30_DAYS,
        "currency": "USD",
        "receipt": f"pro_onetime_{user.id}",
        "notes": {
            "user_id": str(user.id),
            "type": "pro_onetime"
        }
    })

    return {
        "order_id": order['id'],
        "razorpay_key": razorpay_config.KEY_ID,
        "amount": pricing.PRO_ONETIME_30_DAYS,
        "currency": "USD"
    }

@router.post("/create-order/bonus-credits")
async def create_bonus_credits_order(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay order for bonus credit pack"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order = client.order.create(data={
        "amount": pricing.BONUS_CREDIT_PACK,
        "currency": "USD",
        "receipt": f"bonus_credits_{user.id}",
        "notes": {
            "user_id": str(user.id),
            "type": "bonus_credits"
        }
    })

    return {
        "order_id": order['id'],
        "razorpay_key": razorpay_config.KEY_ID,
        "amount": pricing.BONUS_CREDIT_PACK,
        "currency": "USD"
    }

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handle Razorpay webhook events"""
    body = await request.body()

    expected_signature = hmac.new(
        razorpay_config.WEBHOOK_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()

    if x_razorpay_signature != expected_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    event = payload.get('event')

    if event == 'subscription.activated':
        subscription = payload['payload']['subscription']['entity']
        user_id = subscription['notes'].get('user_id')
        if user_id:
            user = crud.get_user(db, UUID(user_id))
            if user:
                upgrade_to_pro(db, user, is_subscription=True, subscription_id=subscription['id'])

    elif event == 'subscription.charged':
        subscription = payload['payload']['subscription']['entity']
        subscription_id = subscription['id']
        user = db.query(User).filter(User.razorpay_subscription_id == subscription_id).first()
        if user and user.subscription_tier != 'pro':
            upgrade_to_pro(db, user, is_subscription=True, subscription_id=subscription_id)

    elif event == 'subscription.cancelled':
        subscription = payload['payload']['subscription']['entity']
        subscription_id = subscription['id']
        user = db.query(User).filter(User.razorpay_subscription_id == subscription_id).first()
        if user:
            downgrade_to_free(db, user)

    elif event == 'order.paid':
        order = payload['payload']['order']['entity']
        user_id = order['notes'].get('user_id')
        payment_type = order['notes'].get('type')

        if user_id:
            user = crud.get_user(db, UUID(user_id))
            if user:
                if payment_type == 'pro_onetime':
                    upgrade_to_pro(db, user, is_subscription=False)
                elif payment_type == 'bonus_credits':
                    add_bonus_credits(db, user)

    return {"status": "success"}
