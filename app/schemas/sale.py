from typing import Optional
from datetime import datetime
from pydantic import condecimal
from .base import BaseSchema, TimestampSchema
from .customer import Customer
from .order import Order


class SaleBase(BaseSchema):
    product_id: int
    order_id: int
    customer_id: int
    quantity: int
    unit_price: condecimal(max_digits=10, decimal_places=2)
    total_amount: condecimal(max_digits=10, decimal_places=2)


class SaleCreate(SaleBase):
    pass


class SaleUpdate(SaleBase):
    product_id: Optional[int] = None
    order_id: Optional[int] = None
    customer_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    total_amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None


class Sale(SaleBase, TimestampSchema):
    id: int
    sale_date: datetime
    order: Optional[Order] = None
    customer: Optional[Customer] = None


# Analytics models
class RevenueAnalytics(BaseSchema):
    period: str
    start_date: datetime
    end_date: datetime
    total_revenue: condecimal(max_digits=10, decimal_places=2)
    total_sales: int
    average_order_value: condecimal(max_digits=10, decimal_places=2)


class CategoryRevenue(BaseSchema):
    category_id: int
    category_name: str
    total_revenue: condecimal(max_digits=10, decimal_places=2)
    total_sales: int
    percentage_of_total: float


class RevenuePeriodComparison(BaseSchema):
    period_1: RevenueAnalytics
    period_2: RevenueAnalytics
    revenue_change_percentage: float
    sales_change_percentage: float 