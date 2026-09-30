from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus, PaymentStatus


class OrderLineRequest(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50)


class OrderCreate(BaseModel):
    items: list[OrderLineRequest] = Field(min_length=1, max_length=30)


class OrderItemPublic(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderPublic(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    stripe_session_id: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemPublic]
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class CheckoutResponse(BaseModel):
    order_id: int
    checkout_url: str
