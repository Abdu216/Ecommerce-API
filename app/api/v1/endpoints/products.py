from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.models import User, Product as ProductModel

router = APIRouter()


@router.post("/", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Create a new product (staff only)."""
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[Product])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get all products with optional filtering."""
    query = db.query(ProductModel)
    
    if category_id:
        query = query.filter(ProductModel.category_id == category_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(ProductModel.name.ilike(search_filter))
    
    return query.offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a specific product by ID."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Update a product (staff only)."""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Delete a product (staff only)."""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"} 