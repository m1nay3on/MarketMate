"""
Payment routes for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.get("/")
async def get_all_payments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments for current user with details"""
    payments = db.query(
        models.Payment,
        models.Order.order_id.label('order_ref'),
        models.Customer.name.label('customer_name'),
        models.Customer.email.label('customer_email')
    ).join(
        models.Order, models.Payment.order_id == models.Order.id
    ).join(
        models.Customer, models.Order.customer_id == models.Customer.id
    ).filter(
        models.Payment.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": payment.Payment.id,
            "payment_id": payment.Payment.payment_id,
            "order_id": payment.order_ref,
            "customer_name": payment.customer_name,
            "email": payment.customer_email,
            "payment_method": payment.Payment.payment_method,
            "status": payment.Payment.status,
            "amount": float(payment.Payment.amount),
            "created_at": payment.Payment.created_at
        }
        for payment in payments
    ]

@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment by ID"""
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id,
        models.Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment

@router.post("/", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: schemas.PaymentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    # Verify order exists
    order = db.query(models.Order).filter(
        models.Order.id == payment_data.order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if payment_id already exists
    existing = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_data.payment_id,
        models.Payment.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment ID already exists"
        )
    
    new_payment = models.Payment(
        **payment_data.dict(),
        user_id=current_user.id,
        status='pending'
    )
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return new_payment

@router.put("/{payment_id}", response_model=schemas.PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: schemas.PaymentUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a payment"""
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id,
        models.Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Update only provided fields
    for field, value in payment_data.dict(exclude_unset=True).items():
        setattr(payment, field, value)
    
    db.commit()
    db.refresh(payment)
    
    return payment

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a payment"""
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id,
        models.Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    db.delete(payment)
    db.commit()
    
    return None
