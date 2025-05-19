from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from app.api import deps
from app.schemas.sale import Sale, SaleCreate, SaleUpdate
from app.models import (
    User, Sale as SaleModel,
    Product as ProductModel,
    Inventory as InventoryModel,
    InventoryHistory as InventoryHistoryModel,
    Order as OrderModel,
    Customer as CustomerModel,
    OrderItem as OrderItemModel
)

router = APIRouter()


@router.post("/", response_model=Sale)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Create a new sale record and update inventory (staff only)."""
    # Check if order exists and belongs to the customer
    order = db.query(OrderModel).filter(
        OrderModel.id == sale.order_id,
        OrderModel.customer_id == sale.customer_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or doesn't belong to the customer")

    # Check if product exists and has enough inventory
    product = db.query(ProductModel).filter(ProductModel.id == sale.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    inventory = db.query(InventoryModel).filter(InventoryModel.product_id == sale.product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    if inventory.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    
    # Create sale record
    db_sale = SaleModel(
        product_id=sale.product_id,
        order_id=sale.order_id,
        customer_id=sale.customer_id,
        quantity=sale.quantity,
        unit_price=sale.unit_price,
        total_amount=sale.total_amount,
        sale_date=datetime.now()
    )
    db.add(db_sale)
    
    # Update inventory
    inventory.quantity -= sale.quantity
    
    # Create inventory history record
    history_record = InventoryHistoryModel(
        inventory_id=inventory.id,
        quantity_change=-sale.quantity,
        reason=f"sale for order #{sale.order_id}"
    )
    db.add(history_record)

    # Create or update order item
    order_item = db.query(OrderItemModel).filter(
        OrderItemModel.order_id == sale.order_id,
        OrderItemModel.product_id == sale.product_id
    ).first()

    if order_item:
        # Update existing order item
        order_item.quantity += sale.quantity
        order_item.total_price += sale.total_amount
    else:
        # Create new order item
        order_item = OrderItemModel(
            order_id=sale.order_id,
            product_id=sale.product_id,
            quantity=sale.quantity,
            unit_price=sale.unit_price,
            total_price=sale.total_amount
        )
        db.add(order_item)
    
    # Update order total
    order.subtotal += sale.total_amount
    order.total = order.subtotal + order.shipping_cost + order.tax
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=List[Sale])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None,
    product_id: int = None,
    category_id: int = None,
    customer_id: int = None,
    order_id: int = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get sales records with optional filtering (staff only)."""
    query = db.query(SaleModel).options(
        joinedload(SaleModel.order),
        joinedload(SaleModel.customer)
    )
    
    if start_date:
        query = query.filter(SaleModel.sale_date >= start_date)
    if end_date:
        query = query.filter(SaleModel.sale_date <= end_date)
    if product_id:
        query = query.filter(SaleModel.product_id == product_id)
    if category_id:
        query = query.join(ProductModel).filter(ProductModel.category_id == category_id)
    if customer_id:
        query = query.filter(SaleModel.customer_id == customer_id)
    if order_id:
        query = query.filter(SaleModel.order_id == order_id)
    
    return query.order_by(SaleModel.sale_date.desc()).offset(skip).limit(limit).all()


@router.get("/{sale_id}", response_model=Sale)
def get_sale(
    sale_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get a specific sale record (staff only)."""
    sale = db.query(SaleModel).options(
        joinedload(SaleModel.order),
        joinedload(SaleModel.customer)
    ).filter(SaleModel.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale 