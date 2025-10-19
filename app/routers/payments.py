from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import stripe
from uuid import UUID
from app.db import get_db, crud
from app.auth import get_current_user
from app.config import stripe_config, pricing
from app.utils.stripe_helpers import create_or_get_stripe_customer, upgrade_to_pro, downgrade_to_free
from app.utils.quota import add_bonus_credits
import os

router = APIRouter(tags=["payments"])
stripe.api_key = stripe_config.SECRET_KEY

@router.post("/checkout/pro-subscription")
async def create_pro_subscription_checkout(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout for recurring Pro subscription"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stripe_customer_id = create_or_get_stripe_customer(user)
    if not user.stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id
        db.commit()

    success_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/payment/cancel"

    checkout_session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': stripe_config.PRO_PRICE_ID,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': str(user.id),
            'type': 'pro_subscription'
        }
    )

    return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

@router.post("/checkout/pro-onetime")
async def create_pro_onetime_checkout(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout for one-time Pro purchase (30 days)"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stripe_customer_id = create_or_get_stripe_customer(user)
    if not user.stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id
        db.commit()

    success_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/payment/cancel"

    checkout_session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Pro Plan - 30 Days',
                    'description': '100 queries for 30 days'
                },
                'unit_amount': pricing.PRO_ONETIME_30_DAYS,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': str(user.id),
            'type': 'pro_onetime'
        }
    )

    return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

@router.post("/checkout/bonus-credits")
async def create_bonus_credits_checkout(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout for bonus credit pack"""
    user = crud.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stripe_customer_id = create_or_get_stripe_customer(user)
    if not user.stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id
        db.commit()

    success_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/payment/cancel"

    checkout_session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Bonus Credit Pack',
                    'description': '10 additional queries (no expiry)'
                },
                'unit_amount': pricing.BONUS_CREDIT_PACK,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': str(user.id),
            'type': 'bonus_credits'
        }
    )

    return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_config.WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        payment_type = session['metadata']['type']

        user = crud.get_user(db, UUID(user_id))
        if not user:
            return {"status": "user not found"}

        if payment_type == 'pro_subscription':
            subscription_id = session.get('subscription')
            upgrade_to_pro(db, user, is_subscription=True, subscription_id=subscription_id)

        elif payment_type == 'pro_onetime':
            upgrade_to_pro(db, user, is_subscription=False)

        elif payment_type == 'bonus_credits':
            add_bonus_credits(db, user)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        if subscription_id:
            user = db.query(crud.User).filter(crud.User.stripe_subscription_id == subscription_id).first()
            if user and user.subscription_tier != 'pro':
                upgrade_to_pro(db, user, is_subscription=True, subscription_id=subscription_id)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']
        user = db.query(crud.User).filter(crud.User.stripe_subscription_id == subscription_id).first()
        if user:
            downgrade_to_free(db, user)

    return {"status": "success"}
