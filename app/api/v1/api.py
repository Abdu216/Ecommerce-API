from fastapi import APIRouter
from app.api.v1.endpoints import (
    products, inventory, sales, analytics,
    auth, customers, orders, addresses
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Customer Management
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])

# Order Management
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])

# Product Management
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

# Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 