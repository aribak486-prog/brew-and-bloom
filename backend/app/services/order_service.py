from collections import Counter
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate


def create_order(db: Session, user: User, payload: OrderCreate) -> Order:
    quantities = Counter()
    for line in payload.items:
        quantities[line.menu_item_id] += line.quantity
    if any(quantity > 50 for quantity in quantities.values()):
        raise HTTPException(status_code=400, detail="Quantity for a menu item cannot exceed 50")

    menu_items = db.scalars(select(MenuItem).where(MenuItem.id.in_(quantities))).all()
    by_id = {item.id: item for item in menu_items}
    missing = set(quantities) - set(by_id)
    if missing:
        raise HTTPException(status_code=404, detail=f"Menu item(s) not found: {', '.join(map(str, sorted(missing)))}")
    unavailable = [item.name for item in menu_items if not item.available]
    if unavailable:
        raise HTTPException(status_code=400, detail=f"Unavailable menu item(s): {', '.join(unavailable)}")

    total = sum((by_id[item_id].price * quantity for item_id, quantity in quantities.items()), Decimal("0.00"))
    order = Order(user_id=user.id, total_amount=total, status=OrderStatus.PENDING, payment_status=PaymentStatus.PENDING)
    order.items = [OrderItem(menu_item_id=item_id, quantity=quantity, price=by_id[item_id].price) for item_id, quantity in quantities.items()]
    db.add(order)
    db.commit()
    return get_order(db, order.id)


def get_order(db: Session, order_id: int) -> Order:
    order = db.scalar(select(Order).options(joinedload(Order.items)).where(Order.id == order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def list_orders(db: Session, user: User) -> list[Order]:
    query = select(Order).options(joinedload(Order.items)).order_by(Order.created_at.desc())
    if user.role != UserRole.ADMIN:
        query = query.where(Order.user_id == user.id)
    return list(db.scalars(query).unique().all())
