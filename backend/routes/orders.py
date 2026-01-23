"""
Order routes for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("/", response_model=List[schemas.OrderDetailResponse])
async def get_all_orders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for current user with details"""
    orders = db.query(
        models.Order,
        models.Customer.name.label('customer_name'),
        models.Customer.address.label('customer_address'),
        models.Item.name.label('item_name')
    ).join(
        models.Customer, models.Order.customer_id == models.Customer.id
    ).join(
        models.Item, models.Order.item_id == models.Item.id
    ).filter(
        models.Order.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": order.Order.id,
            "order_id": order.Order.order_id,
            "customer_name": order.customer_name,
            "item_name": order.item_name,
            "customer_address": order.customer_address or "N/A",
            "payment_method": order.Order.payment_method,
            "status": order.Order.status,
            "created_at": order.Order.created_at
        }
        for order in orders
    ]

@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order by ID"""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    # Verify customer exists
    customer = db.query(models.Customer).filter(
        models.Customer.id == order_data.customer_id,
        models.Customer.user_id == current_user.id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Verify item exists
    item = db.query(models.Item).filter(
        models.Item.id == order_data.item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Check if order_id already exists
    existing = db.query(models.Order).filter(
        models.Order.order_id == order_data.order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID already exists"
        )
    
    new_order = models.Order(
        **order_data.dict(),
        user_id=current_user.id,
        status='pending'
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.put("/{order_id}", response_model=schemas.OrderResponse)
async def update_order(
    order_id: int,
    order_data: schemas.OrderUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an order"""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update only provided fields
    for field, value in order_data.dict(exclude_unset=True).items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an order"""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    db.delete(order)
    db.commit()
    
    return None
