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

@router.get("/my-payments")
async def get_my_customer_payments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payments for orders where the current user is the customer"""
    # Find ALL customer records for this user (they might have records under different admins)
    customers = db.query(models.Customer).filter(
        models.Customer.email == current_user.email
    ).all()
    
    if not customers:
        return []
    
    customer_ids = [c.id for c in customers]
    
    # Get payments for all of this customer's orders
    payments = db.query(
        models.Payment,
        models.Order.order_id.label('order_ref'),
        models.Order.id.label('order_db_id')
    ).join(
        models.Order, models.Payment.order_id == models.Order.id
    ).filter(
        models.Order.customer_id.in_(customer_ids)
    ).all()
    
    return [
        {
            "id": payment.Payment.id,
            "payment_id": payment.Payment.payment_id,
            "order_id": payment.order_ref,
            "order_db_id": payment.order_db_id,
            "payment_method": payment.Payment.payment_method,
            "status": payment.Payment.status.value if hasattr(payment.Payment.status, 'value') else str(payment.Payment.status),
            "amount": float(payment.Payment.amount),
            "created_at": payment.Payment.created_at
        }
        for payment in payments
    ]

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
    # Verify order exists - check if user is the order owner OR the customer
    order = db.query(models.Order).filter(
        models.Order.id == payment_data.order_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if current user is authorized (either order owner or the customer)
    customer = db.query(models.Customer).filter(
        models.Customer.id == order.customer_id
    ).first()
    
    is_order_owner = order.user_id == current_user.id
    is_customer = customer and customer.email == current_user.email
    
    if not (is_order_owner or is_customer):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for this order"
        )
    
    # Check if payment already exists for this order
    existing_payment = db.query(models.Payment).filter(
        models.Payment.order_id == payment_data.order_id
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this order"
        )
    
    # Use the order's user_id (admin) for the payment
    new_payment = models.Payment(
        **payment_data.dict(),
        user_id=order.user_id,  # Use order owner's ID
        status=payment_data.status if hasattr(payment_data, 'status') else 'pending'
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
    print(f"\n💳 [UPDATE-PAYMENT] Payment ID: {payment_id}, User: {current_user.email}")
    print(f"💳 [UPDATE-PAYMENT] Payment data: {payment_data.dict(exclude_unset=True)}")
    
    # Get payment first
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id
    ).first()
    
    if not payment:
        print(f"💳 [UPDATE-PAYMENT] ❌ Payment {payment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    print(f"💳 [UPDATE-PAYMENT] Found payment: OrderID={payment.order_id}, Status={payment.status}")
    
    # Check authorization - user must be payment owner OR the customer
    order = db.query(models.Order).filter(
        models.Order.id == payment.order_id
    ).first()
    
    if order:
        customer = db.query(models.Customer).filter(
            models.Customer.id == order.customer_id
        ).first()
        
        is_payment_owner = payment.user_id == current_user.id
        is_customer = customer and customer.email == current_user.email
        
        print(f"💳 [UPDATE-PAYMENT] Auth check: is_payment_owner={is_payment_owner}, is_customer={is_customer}")
        
        if not (is_payment_owner or is_customer):
            print(f"💳 [UPDATE-PAYMENT] ❌ Not authorized")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this payment"
            )
    
    # Update only provided fields
    print(f"💳 [UPDATE-PAYMENT] Updating fields...")
    for field, value in payment_data.dict(exclude_unset=True).items():
        print(f"💳 [UPDATE-PAYMENT]   {field} = {value}")
        setattr(payment, field, value)
    
    # If payment is marked as paid, update order status to "paid" (not shipped yet)
    # Shipping will be created when admin confirms the order
    if payment_data.status and payment_data.status.lower() in ['paid', 'completed']:
        print(f"💳 [UPDATE-PAYMENT] Payment marked as paid, updating order status to 'paid'...")
        order = db.query(models.Order).filter(
            models.Order.id == payment.order_id
        ).first()
        
        if order:
            # Set order to "paid" - admin will see this and can confirm shipping
            order.status = models.OrderStatus.paid
            print(f"💳 [UPDATE-PAYMENT] Order {order.order_id} status updated to 'paid'")
    
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
