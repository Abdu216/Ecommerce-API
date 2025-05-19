from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.schemas.inventory import (
    Inventory, InventoryCreate, InventoryUpdate,
    InventoryHistory, InventoryHistoryCreate, InventoryWithHistory
)
from app.models import User, Inventory as InventoryModel, Product as ProductModel, InventoryHistory as InventoryHistoryModel

router = APIRouter()


@router.post("/", response_model=Inventory)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Create a new inventory record (staff only)."""
    # Check if product exists
    product = db.query(ProductModel).filter(ProductModel.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if inventory already exists for this product
    existing_inventory = db.query(InventoryModel).filter(
        InventoryModel.product_id == inventory.product_id
    ).first()
    if existing_inventory:
        raise HTTPException(status_code=400, detail="Inventory already exists for this product")
    
    db_inventory = InventoryModel(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.get("/", response_model=List[Inventory])
def get_inventories(
    skip: int = 0,
    limit: int = 100,
    low_stock: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get all inventory records with optional low stock filter (staff only)."""
    query = db.query(InventoryModel)
    
    if low_stock:
        query = query.filter(InventoryModel.quantity <= InventoryModel.low_stock_threshold)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{inventory_id}", response_model=InventoryWithHistory)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get a specific inventory record with its history (staff only)."""
    inventory = db.query(InventoryModel).filter(InventoryModel.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.put("/{inventory_id}", response_model=Inventory)
def update_inventory(
    inventory_id: int,
    inventory_update: InventoryUpdate,
    reason: str = Query(..., description="Reason for inventory update"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Update an inventory record and log the change (staff only)."""
    db_inventory = db.query(InventoryModel).filter(InventoryModel.id == inventory_id).first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    update_data = inventory_update.model_dump(exclude_unset=True)
    
    # Create inventory history record if quantity is being updated
    if "quantity" in update_data:
        quantity_change = update_data["quantity"] - db_inventory.quantity
        history_record = InventoryHistoryModel(
            inventory_id=inventory_id,
            quantity_change=quantity_change,
            reason=reason
        )
        db.add(history_record)
    
    # Update inventory record
    for field, value in update_data.items():
        setattr(db_inventory, field, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.get("/{inventory_id}/history", response_model=List[InventoryHistory])
def get_inventory_history(
    inventory_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get the history of changes for a specific inventory record (staff only)."""
    # Check if inventory exists
    inventory = db.query(InventoryModel).filter(InventoryModel.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    history = db.query(InventoryHistoryModel)\
        .filter(InventoryHistoryModel.inventory_id == inventory_id)\
        .order_by(InventoryHistoryModel.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return history 