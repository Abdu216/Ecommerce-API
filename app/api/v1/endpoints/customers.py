from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.schemas.customer import (
    Customer, CustomerCreate, CustomerUpdate,
    CustomerWithOrders
)
from app.models import (
    User, Customer as CustomerModel,
    Order as OrderModel,
    Address as AddressModel,
    UserRole
)
from app.core.security import get_password_hash

router = APIRouter()


@router.post("/", response_model=Customer)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Create a new customer (staff only)."""
    # Check if user with email exists
    if db.query(User).filter(User.email == customer.user.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    db_user = User(
        email=customer.user.email,
        full_name=customer.user.full_name,
        hashed_password=get_password_hash(customer.user.password),
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db.add(db_user)
    db.flush()
    
    # Create customer profile
    db_customer = CustomerModel(
        user_id=db_user.id,
        phone=customer.phone,
        default_shipping_address_id=customer.default_shipping_address_id,
        default_billing_address_id=customer.default_billing_address_id
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return db_customer


@router.get("/", response_model=List[Customer])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get all customers (staff only)."""
    query = db.query(CustomerModel)
    
    if search:
        search_filter = f"%{search}%"
        query = query.join(User).filter(
            (User.email.ilike(search_filter)) |
            (User.full_name.ilike(search_filter)) |
            (CustomerModel.phone.ilike(search_filter))
        )
    
    return query.offset(skip).limit(limit).all()


@router.get("/me", response_model=CustomerWithOrders)
def get_current_customer(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get current customer profile with orders."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=400,
            detail="User is not a customer"
        )
    
    customer = db.query(CustomerModel).filter(
        CustomerModel.user_id == current_user.id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )
    
    return customer


@router.get("/{customer_id}", response_model=CustomerWithOrders)
def get_customer(
    customer_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get a specific customer by ID (staff only)."""
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Update a customer (staff only)."""
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Update customer fields
    update_data = customer_update.model_dump(exclude_unset=True)
    if "user" in update_data:
        user_data = update_data.pop("user")
        user = db.query(User).filter(User.id == db_customer.user_id).first()
        for field, value in user_data.items():
            if field != "password":  # Handle password separately if needed
                setattr(user, field, value)
    
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Delete a customer (staff only)."""
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Delete associated user
    user = db.query(User).filter(User.id == db_customer.user_id).first()
    if user:
        db.delete(user)  # This should cascade delete the customer due to foreign key
    
    db.commit()
    return {"message": "Customer deleted successfully"} 