from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.api import deps
from app.schemas.order import (
    Order, OrderCreate, OrderUpdate,
    OrderResponse, OrderListResponse
)
from app.models import (
    User, Order as OrderModel,
    Customer as CustomerModel,
    OrderItem as OrderItemModel,
    Product as ProductModel,
    Payment as PaymentModel,
    OrderStatus, PaymentStatus
)

router = APIRouter()


def calculate_payment_status(order: OrderModel) -> PaymentStatus:
    """Helper function to calculate payment status from order payments."""
    if not order.payments:
        return PaymentStatus.PENDING
    
    total_paid = sum(payment.amount for payment in order.payments if payment.status == PaymentStatus.COMPLETED)
    
    if total_paid >= order.total:
        return PaymentStatus.COMPLETED
    elif total_paid > 0:
        return PaymentStatus.PARTIAL
    else:
        return PaymentStatus.PENDING


@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create a new order."""
    # Verify customer exists and matches current user or staff permission
    customer = db.query(CustomerModel).filter(CustomerModel.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized to create order for this customer")
    
    # Calculate order totals
    subtotal = 0
    for item in order.items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        item_total = product.price * item.quantity
        subtotal += item_total
    
    # Create order
    db_order = OrderModel(
        customer_id=order.customer_id,
        shipping_address_id=order.shipping_address_id,
        billing_address_id=order.billing_address_id,
        subtotal=subtotal,
        shipping_cost=order.shipping_cost,
        tax=order.tax,
        total=subtotal + order.shipping_cost + order.tax,
        status=OrderStatus.PENDING,
        notes=order.notes
    )
    db.add(db_order)
    db.flush()  # Get order ID without committing
    
    # Create order items
    for item in order.items:
        db_item = OrderItemModel(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    
    return OrderResponse(
        **db_order.__dict__,
        total_items=len(order.items),
        payment_status=PaymentStatus.PENDING
    )


@router.get("/", response_model=OrderListResponse)
def get_orders(
    skip: int = 0,
    limit: int = 100,
    customer_id: int = None,
    status: OrderStatus = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get all orders with optional filtering."""
    query = db.query(OrderModel).options(
        joinedload(OrderModel.items),
        joinedload(OrderModel.payments)
    )
    
    # Filter by customer if specified or if regular user
    if customer_id:
        query = query.filter(OrderModel.customer_id == customer_id)
    elif not current_user.is_staff:
        # Regular users can only see their own orders
        customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        query = query.filter(OrderModel.customer_id == customer.id)
    
    if status:
        query = query.filter(OrderModel.status == status)
    
    total = query.count()
    orders = query.order_by(OrderModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return OrderListResponse(
        total=total,
        page=skip // limit + 1,
        size=limit,
        orders=[
            OrderResponse(
                **order.__dict__,
                total_items=len(order.items),
                payment_status=calculate_payment_status(order)
            )
            for order in orders
        ]
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a specific order."""
    order = db.query(OrderModel).options(
        joinedload(OrderModel.items),
        joinedload(OrderModel.payments)
    ).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permission
    if not current_user.is_staff:
        customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
        if not customer or order.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return OrderResponse(
        **order.__dict__,
        total_items=len(order.items),
        payment_status=calculate_payment_status(order)
    )


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Update an order (staff only)."""
    db_order = db.query(OrderModel).options(
        joinedload(OrderModel.items),
        joinedload(OrderModel.payments)
    ).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order items if provided
    if order_update.items:
        # Remove existing items
        db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).delete()
        
        # Add new items
        subtotal = 0
        for item in order_update.items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            item_total = product.price * item.quantity
            subtotal += item_total
            
            db_item = OrderItemModel(
                order_id=order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            db.add(db_item)
        
        # Update order totals
        db_order.subtotal = subtotal
        db_order.total = subtotal + db_order.shipping_cost + db_order.tax
    
    # Update other fields
    update_data = order_update.model_dump(exclude={'items'}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    
    return OrderResponse(
        **db_order.__dict__,
        total_items=len(db_order.items),
        payment_status=calculate_payment_status(db_order)
    )


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Delete an order (staff only)."""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Delete associated order items first
    db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).delete()
    
    # Delete associated payments
    db.query(PaymentModel).filter(PaymentModel.order_id == order_id).delete()
    
    # Delete the order
    db.delete(db_order)
    db.commit()
    
    return {"message": "Order deleted successfully"} 