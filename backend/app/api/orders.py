from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.database.connection import get_db
from app.models.order import OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderPublic, OrderStatusUpdate
from app.services.order_service import create_order, get_order, list_orders

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def place_order(payload: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customer accounts can place orders")
    return {"success": True, "data": OrderPublic.model_validate(create_order(db, user, payload))}


@router.get("")
def my_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"success": True, "data": [OrderPublic.model_validate(order) for order in list_orders(db, user)]}


@router.get("/{order_id}")
def order_detail(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = get_order(db, order_id)
    if user.role != UserRole.ADMIN and order.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot access this order")
    return {"success": True, "data": OrderPublic.model_validate(order)}


@router.patch("/{order_id}/status")
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    order = get_order(db, order_id)
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return {"success": True, "data": OrderPublic.model_validate(order)}
