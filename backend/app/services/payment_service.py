import stripe
from fastapi import HTTPException

from app.core.config import settings
from app.models.order import Order


def _configured_test_key() -> str:
    key = settings.stripe_secret_key
    if not key.startswith("sk_test_"):
        raise HTTPException(status_code=503, detail="Stripe TEST MODE is not configured. Set STRIPE_SECRET_KEY to an sk_test_ key.")
    return key


def create_checkout_session(order: Order, frontend_url: str) -> stripe.checkout.Session:
    stripe.api_key = _configured_test_key()
    try:
        return stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(item.price * 100),
                    "product_data": {"name": item.menu_item.name},
                },
                "quantity": item.quantity,
            } for item in order.items],
            metadata={"order_id": str(order.id), "user_id": str(order.user_id)},
            success_url=f"{frontend_url.rstrip('/')}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url.rstrip('/')}/?checkout=cancelled&order_id={order.id}",
        )
    except stripe.StripeError as exc:
        raise HTTPException(status_code=502, detail="Could not create Stripe checkout session") from exc


def verify_webhook(payload: bytes, signature: str | None) -> stripe.Event:
    _configured_test_key()
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    try:
        return stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature or payload") from exc
