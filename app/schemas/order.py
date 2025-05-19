from typing import Optional, List
from datetime import datetime
from pydantic import condecimal
from .base import BaseSchema, TimestampSchema
from app.models import OrderStatus, PaymentStatus


class OrderItemBase(BaseSchema):
    product_id: int
    quantity: int
    unit_price: condecimal(max_digits=10, decimal_places=2)
    total_price: condecimal(max_digits=10, decimal_places=2)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(OrderItemBase):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    total_price: Optional[condecimal(max_digits=10, decimal_places=2)] = None


class OrderItem(OrderItemBase, TimestampSchema):
    id: int
    order_id: int


class PaymentBase(BaseSchema):
    amount: condecimal(max_digits=10, decimal_places=2)
    payment_method: str
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    payment_method: Optional[str] = None
    status: Optional[PaymentStatus] = None


class Payment(PaymentBase, TimestampSchema):
    id: int
    order_id: int
    payment_date: datetime


class OrderBase(BaseSchema):
    customer_id: int
    shipping_address_id: int
    billing_address_id: int
    subtotal: condecimal(max_digits=10, decimal_places=2)
    shipping_cost: condecimal(max_digits=10, decimal_places=2)
    tax: condecimal(max_digits=10, decimal_places=2)
    total: condecimal(max_digits=10, decimal_places=2)
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseSchema):
    shipping_address_id: Optional[int] = None
    billing_address_id: Optional[int] = None
    subtotal: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    shipping_cost: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    tax: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    total: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    status: Optional[OrderStatus] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None


class Order(OrderBase, TimestampSchema):
    id: int
    order_date: datetime
    items: List[OrderItem] = []
    payments: List[Payment] = []


# Response models for order operations
class OrderResponse(Order):
    total_items: int
    payment_status: PaymentStatus


class OrderListResponse(BaseSchema):
    total: int
    page: int
    size: int
    orders: List[OrderResponse] 