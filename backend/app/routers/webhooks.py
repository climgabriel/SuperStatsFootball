from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
import stripe

from app.core.config import settings
from app.core.dependencies import get_db
from app.models.user import User
from app.utils.logger import logger

router = APIRouter()

# Configure Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks for subscription events.

    Processes:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe not configured, ignoring webhook")
        return {"status": "ignored", "reason": "Stripe not configured"}

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Received Stripe webhook: {event_type}")

    if event_type == "customer.subscription.created":
        # Handle new subscription
        handle_subscription_created(data, db)

    elif event_type == "customer.subscription.updated":
        # Handle subscription update
        handle_subscription_updated(data, db)

    elif event_type == "customer.subscription.deleted":
        # Handle subscription cancellation
        handle_subscription_deleted(data, db)

    elif event_type == "invoice.payment_succeeded":
        # Handle successful payment
        logger.info(f"Payment succeeded for customer {data.get('customer')}")

    elif event_type == "invoice.payment_failed":
        # Handle failed payment
        handle_payment_failed(data, db)

    return {"status": "received"}


def handle_subscription_created(data: dict, db: Session):
    """Handle new subscription creation."""
    customer_id = data.get("customer")
    subscription_id = data.get("id")
    price_id = data["items"]["data"][0]["price"]["id"]

    # Find user by Stripe customer ID
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        # Map price ID to tier
        tier = get_tier_from_price_id(price_id)

        user.subscription_id = subscription_id
        user.tier = tier
        user.subscription_status = "active"
        db.commit()

        logger.info(f"Subscription created for user {user.email}: {tier}")


def handle_subscription_updated(data: dict, db: Session):
    """Handle subscription update."""
    customer_id = data.get("customer")
    subscription_id = data.get("id")
    status = data.get("status")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.subscription_status = status
        if status != "active":
            user.tier = "free"
        db.commit()

        logger.info(f"Subscription updated for user {user.email}: {status}")


def handle_subscription_deleted(data: dict, db: Session):
    """Handle subscription cancellation."""
    customer_id = data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.tier = "free"
        user.subscription_status = "canceled"
        user.subscription_id = None
        db.commit()

        logger.info(f"Subscription canceled for user {user.email}")


def handle_payment_failed(data: dict, db: Session):
    """Handle failed payment."""
    customer_id = data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.subscription_status = "past_due"
        db.commit()

        logger.warning(f"Payment failed for user {user.email}")


def get_tier_from_price_id(price_id: str) -> str:
    """Map Stripe price ID to subscription tier."""
    price_tier_map = {
        settings.STRIPE_PRICE_ID_STARTER: "starter",
        settings.STRIPE_PRICE_ID_PRO: "pro",
        settings.STRIPE_PRICE_ID_PREMIUM: "premium",
        settings.STRIPE_PRICE_ID_ULTIMATE: "ultimate"
    }

    return price_tier_map.get(price_id, "free")
