from typing import Optional, List
from pydantic import EmailStr, constr
from datetime import datetime
from .base import BaseSchema, TimestampSchema
from app.models import UserRole


class UserBase(BaseSchema):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase, TimestampSchema):
    id: int


class AddressBase(BaseSchema):
    street_address: str
    city: str
    state: Optional[str] = None
    postal_code: constr(min_length=4, max_length=10)
    country: str
    is_default: Optional[bool] = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AddressBase):
    pass


class Address(AddressBase, TimestampSchema):
    id: int


class CustomerBase(BaseSchema):
    phone: Optional[str] = None
    default_shipping_address_id: Optional[int] = None
    default_billing_address_id: Optional[int] = None


class CustomerCreate(CustomerBase):
    user: UserCreate


class CustomerUpdate(CustomerBase):
    user: Optional[UserUpdate] = None


class Customer(CustomerBase):
    id: int
    user_id: int
    user: User
    addresses: List[Address] = []
    billing_addresses: List[Address] = []


# Token schemas for authentication
class Token(BaseSchema):
    access_token: str
    token_type: str


class TokenPayload(BaseSchema):
    sub: int  # user_id
    exp: datetime
    role: UserRole 