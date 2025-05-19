from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas import Token, User, UserCreate, Customer, CustomerCreate
from app.models import User as UserModel
from app.models import Customer as CustomerModel

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register/customer", response_model=Customer)
def register_customer(
    *,
    db: Session = Depends(deps.get_db),
    customer_in: CustomerCreate,
) -> Any:
    """
    Register a new customer.
    """
    user = db.query(UserModel).filter(UserModel.email == customer_in.user.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    # Create user
    user = UserModel(
        email=customer_in.user.email,
        hashed_password=security.get_password_hash(customer_in.user.password),
        full_name=customer_in.user.full_name,
        role=customer_in.user.role,
        is_active=True
    )
    db.add(user)
    db.flush()  # Get user ID without committing

    # Create customer profile
    customer = CustomerModel(
        user_id=user.id,
        phone=customer_in.phone,
        default_shipping_address_id=customer_in.default_shipping_address_id,
        default_billing_address_id=customer_in.default_billing_address_id
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer


@router.post("/register/staff", response_model=User)
def register_staff(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Register a new staff member (Admin only).
    """
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    user = UserModel(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 