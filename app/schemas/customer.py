from typing import Optional, List
from .base import BaseSchema
from .user import User, UserCreate, UserUpdate
from .address import Address
from .order import Order


class CustomerBase(BaseSchema):
    phone: Optional[str] = None
    default_shipping_address_id: Optional[int] = None
    default_billing_address_id: Optional[int] = None


class CustomerCreate(CustomerBase):
    user: UserCreate


class CustomerUpdate(CustomerBase):
    phone: Optional[str] = None
    default_shipping_address_id: Optional[int] = None
    default_billing_address_id: Optional[int] = None
    user: Optional[UserUpdate] = None


class Customer(CustomerBase):
    id: int
    user_id: int
    user: User
    default_shipping_address: Optional[Address] = None
    default_billing_address: Optional[Address] = None


class CustomerWithOrders(Customer):
    orders: List[Order] = []