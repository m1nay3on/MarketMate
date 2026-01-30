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

@router.get("/my-shipping")
async def get_my_customer_shipping(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get shipping records where the current user is the customer"""
    # Find ALL customer records for this user
    customers = db.query(models.Customer).filter(
        models.Customer.email == current_user.email
    ).all()
    
    if not customers:
        return []
    
    customer_ids = [c.id for c in customers]
    
    # Get shipping for orders where this user is the customer (across all customer records)
    shipping_records = db.query(
        models.Shipping,
        models.Order.order_id.label('order_ref'),
        models.Item.name.label('item_name'),
        models.Item.price.label('item_price')
    ).join(
        models.Order, models.Shipping.order_id == models.Order.id
    ).join(
        models.Item, models.Order.item_id == models.Item.id
    ).filter(
        models.Order.customer_id.in_(customer_ids)
    ).all()
    
    result = []
    for record in shipping_records:
        # Try to find payment for this order to get total amount
        payment = db.query(models.Payment).filter(
            models.Payment.order_id == record.Shipping.order_id
        ).first()
        
        total_amount = float(record.item_price) if record.item_price else 0
        if payment:
            total_amount = float(payment.amount)
        
        result.append({
            "id": record.Shipping.id,
            "shipping_id": record.Shipping.shipping_id,
            "order_id": record.order_ref,
            "item_name": record.item_name,
            "courier": record.Shipping.courier,
            "address": record.Shipping.address,
            "status": record.Shipping.status.value if hasattr(record.Shipping.status, 'value') else str(record.Shipping.status),
            "total_amount": total_amount,
            "created_at": record.Shipping.created_at
        })
    
    return result

@router.get("/")
async def get_all_shipping(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active shipping records for current user (excludes delivered/completed)"""
    shipping_records = db.query(
        models.Shipping,
        models.Order.order_id.label('order_ref')
    ).join(
        models.Order, models.Shipping.order_id == models.Order.id
    ).filter(
        models.Shipping.user_id == current_user.id,
        # Only show active shipments - exclude delivered orders
        models.Shipping.status.notin_([models.ShippingStatus.delivered])
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
    print(f"\n🚚 [UPDATE-SHIPPING] Shipping ID: {shipping_id}, User: {current_user.email}")
    print(f"🚚 [UPDATE-SHIPPING] Update data: {shipping_data.dict(exclude_unset=True)}")
    
    shipping = db.query(models.Shipping).filter(
        models.Shipping.id == shipping_id,
        models.Shipping.user_id == current_user.id
    ).first()
    
    if not shipping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping record not found"
        )
    
    print(f"🚚 [UPDATE-SHIPPING] Found shipping: {shipping.shipping_id}, order_id: {shipping.order_id}")
    
    # Check if we're updating to shipped status
    new_status = shipping_data.dict(exclude_unset=True).get('status')
    
    # Update only provided fields with proper enum conversion
    for field, value in shipping_data.dict(exclude_unset=True).items():
        if field == 'status' and value:
            # Convert string to ShippingStatus enum
            status_value = value.lower()
            try:
                shipping.status = models.ShippingStatus(status_value)
                print(f"🚚 [UPDATE-SHIPPING] Set status to enum: {shipping.status}")
            except ValueError:
                print(f"🚚 [UPDATE-SHIPPING] Invalid status value: {status_value}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status value: {status_value}"
                )
        else:
            setattr(shipping, field, value)
    
    # If shipping status is being set to shipped, also update the order status
    if new_status and new_status.lower() == 'shipped':
        print(f"🚚 [UPDATE-SHIPPING] Shipping marked as shipped, updating order status...")
        order = db.query(models.Order).filter(
            models.Order.id == shipping.order_id
        ).first()
        
        if order:
            order.status = models.OrderStatus.shipped
            print(f"🚚 [UPDATE-SHIPPING] Order {order.order_id} status updated to shipped")
    
    # If shipping status is being set to delivered, also update order to completed and payment to paid
    if new_status and new_status.lower() == 'delivered':
        print(f"🚚 [UPDATE-SHIPPING] Shipping marked as delivered, updating order and payment...")
        order = db.query(models.Order).filter(
            models.Order.id == shipping.order_id
        ).first()
        
        if order:
            order.status = models.OrderStatus.completed
            print(f"🚚 [UPDATE-SHIPPING] Order {order.order_id} status updated to completed")
            
            # Also update payment status to paid
            payment = db.query(models.Payment).filter(
                models.Payment.order_id == order.id
            ).first()
            
            if payment:
                payment.status = models.PaymentStatus.paid
                print(f"🚚 [UPDATE-SHIPPING] Payment {payment.payment_id} status updated to paid")
    
    db.commit()
    db.refresh(shipping)
    
    print(f"🚚 [UPDATE-SHIPPING] Shipping updated successfully")
    
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
