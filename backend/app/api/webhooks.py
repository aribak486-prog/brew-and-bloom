from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.services.payment_service import verify_webhook

router = APIRouter(prefix="/api/webhooks", tags=["payments"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    event = verify_webhook(await request.body(), request.headers.get("stripe-signature"))
    if event.type == "checkout.session.completed":
        session = event.data.object
        order_id = (session.get("metadata") or {}).get("order_id")
        order = db.scalar(select(Order).where(Order.id == int(order_id))) if order_id else None
        if order is not None and session.get("payment_status") == "paid":
            order.payment_status = PaymentStatus.PAID
            order.status = OrderStatus.CONFIRMED
            order.stripe_session_id = session.id
            db.commit()
    elif event.type == "checkout.session.expired":
        session = event.data.object
        order_id = (session.get("metadata") or {}).get("order_id")
        order = db.scalar(select(Order).where(Order.id == int(order_id))) if order_id else None
        if order is not None and order.payment_status == PaymentStatus.PENDING:
            order.payment_status = PaymentStatus.FAILED
            order.stripe_session_id = session.id
            db.commit()
    return {"success": True, "data": {"received": True}}
