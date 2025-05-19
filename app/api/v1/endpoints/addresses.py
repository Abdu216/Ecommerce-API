from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.address import (
    Address, AddressCreate, AddressUpdate
)
from app.models import (
    User, Address as AddressModel,
    Customer as CustomerModel
)

router = APIRouter()


@router.post("/", response_model=Address)
def create_address(
    address: AddressCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create a new address."""
    # Get customer profile
    customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    # Create address
    db_address = AddressModel(
        customer_id=customer.id,
        **address.model_dump()
    )
    db.add(db_address)
    
    # Set as default if requested
    if address.is_default:
        if db_address.is_shipping:
            customer.default_shipping_address_id = db_address.id
        if db_address.is_billing:
            customer.default_billing_address_id = db_address.id
    
    db.commit()
    db.refresh(db_address)
    return db_address


@router.get("/", response_model=List[Address])
def get_addresses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get all addresses for the current user."""
    # Get customer profile
    customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    return db.query(AddressModel).filter(AddressModel.customer_id == customer.id).all()


@router.get("/{address_id}", response_model=Address)
def get_address(
    address_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a specific address."""
    # Get customer profile
    customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    # Get address and verify ownership
    address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.customer_id == customer.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    return address


@router.put("/{address_id}", response_model=Address)
def update_address(
    address_id: int,
    address_update: AddressUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update an address."""
    # Get customer profile
    customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    # Get address and verify ownership
    db_address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.customer_id == customer.id
    ).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Update address fields
    update_data = address_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_address, field, value)
    
    # Update default address settings if requested
    if address_update.is_default:
        if db_address.is_shipping:
            customer.default_shipping_address_id = db_address.id
        if db_address.is_billing:
            customer.default_billing_address_id = db_address.id
    
    db.commit()
    db.refresh(db_address)
    return db_address


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Delete an address."""
    # Get customer profile
    customer = db.query(CustomerModel).filter(CustomerModel.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    # Get address and verify ownership
    address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.customer_id == customer.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Remove as default if it was set
    if customer.default_shipping_address_id == address_id:
        customer.default_shipping_address_id = None
    if customer.default_billing_address_id == address_id:
        customer.default_billing_address_id = None
    
    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"} 