from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.database.connection import get_db
from app.models.order import Order
from app.models.user import User, UserRole
from app.schemas.order import CheckoutResponse, OrderCreate
from app.services.order_service import create_order
from app.services.payment_service import create_checkout_session

router = APIRouter(prefix="/api", tags=["checkout"])


@router.post("/checkout")
def checkout(payload: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customer accounts can check out")
    order = create_order(db, user, payload)
    session = create_checkout_session(order, settings.frontend_url)
    order.stripe_session_id = session.id
    db.commit()
    response = CheckoutResponse(order_id=order.id, checkout_url=session.url)
    return {"success": True, "data": response}
