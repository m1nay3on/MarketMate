"""
Shipping routes for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/shipping", tags=["Shipping"])

@router.get("/")
async def get_all_shipping(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all shipping records for current user with order details"""
    shipping_records = db.query(
        models.Shipping,
        models.Order.order_id.label('order_ref')
    ).join(
        models.Order, models.Shipping.order_id == models.Order.id
    ).filter(
        models.Shipping.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": record.Shipping.id,
            "shipping_id": record.Shipping.shipping_id,
            "order_id": record.order_ref,
            "courier": record.Shipping.courier,
            "address": record.Shipping.address,
            "status": record.Shipping.status,
            "created_at": record.Shipping.created_at
        }
        for record in shipping_records
    ]

@router.get("/{shipping_id}", response_model=schemas.ShippingResponse)
async def get_shipping(
    shipping_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific shipping record by ID"""
    shipping = db.query(models.Shipping).filter(
        models.Shipping.id == shipping_id,
        models.Shipping.user_id == current_user.id
    ).first()
    
    if not shipping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping record not found"
        )
    
    return shipping

@router.post("/", response_model=schemas.ShippingResponse, status_code=status.HTTP_201_CREATED)
async def create_shipping(
    shipping_data: schemas.ShippingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new shipping record"""
    # Verify order exists
    order = db.query(models.Order).filter(
        models.Order.id == shipping_data.order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if shipping_id already exists
    existing = db.query(models.Shipping).filter(
        models.Shipping.shipping_id == shipping_data.shipping_id,
        models.Shipping.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shipping ID already exists"
        )
    
    new_shipping = models.Shipping(
        **shipping_data.dict(),
        user_id=current_user.id,
        status='preparing'
    )
    
    db.add(new_shipping)
    db.commit()
    db.refresh(new_shipping)
    
    return new_shipping

@router.put("/{shipping_id}", response_model=schemas.ShippingResponse)
async def update_shipping(
    shipping_id: int,
    shipping_data: schemas.ShippingUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a shipping record"""
    shipping = db.query(models.Shipping).filter(
        models.Shipping.id == shipping_id,
        models.Shipping.user_id == current_user.id
    ).first()
    
    if not shipping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping record not found"
        )
    
    # Update only provided fields
    for field, value in shipping_data.dict(exclude_unset=True).items():
        setattr(shipping, field, value)
    
    db.commit()
    db.refresh(shipping)
    
    return shipping

@router.delete("/{shipping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipping(
    shipping_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a shipping record"""
    shipping = db.query(models.Shipping).filter(
        models.Shipping.id == shipping_id,
        models.Shipping.user_id == current_user.id
    ).first()
    
    if not shipping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping record not found"
        )
    
    db.delete(shipping)
    db.commit()
    
    return None
