from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(..., ge=1)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=1)


class InventoryInDB(InventoryBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class Inventory(InventoryInDB):
    pass


class InventoryHistoryBase(BaseModel):
    inventory_id: int
    quantity_change: int
    reason: str = Field(..., min_length=1, max_length=100)


class InventoryHistoryCreate(InventoryHistoryBase):
    pass


class InventoryHistoryInDB(InventoryHistoryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class InventoryHistory(InventoryHistoryInDB):
    pass


class InventoryWithHistory(Inventory):
    inventory_history: List[InventoryHistory]

    class Config:
        from_attributes = True 