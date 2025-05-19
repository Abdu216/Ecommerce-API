from typing import Optional
from pydantic import constr
from .base import BaseSchema, TimestampSchema


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
    street_address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[constr(min_length=4, max_length=10)] = None
    country: Optional[str] = None


class Address(AddressBase, TimestampSchema):
    id: int 