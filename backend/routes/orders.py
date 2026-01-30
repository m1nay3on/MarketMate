"""
Order routes for CRUD operations
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/checkout", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
async def customer_checkout(
    checkout_data: schemas.CustomerCheckout,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customer checkout - creates order for the logged-in user"""
    # First, verify item exists to get the item owner (admin)
    item = db.query(models.Item).filter(
        models.Item.id == checkout_data.item_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    admin_user_id = item.user_id  # The admin who owns this item
    
    # Find or create customer record for this user (under the admin)
    customer = db.query(models.Customer).filter(
        models.Customer.email == current_user.email,
        models.Customer.user_id == admin_user_id
    ).first()
    
    if not customer:
        # Create customer record for this user under the admin
        customer_id = f"CUS-{uuid.uuid4().hex[:8].upper()}"
        customer = models.Customer(
            customer_id=customer_id,
            name=current_user.username,
            email=current_user.email,
            address="Address not provided",  # Default address
            user_id=admin_user_id,  # Customer belongs to admin
            status=models.CustomerStatus.active
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    # Generate unique order ID
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Map payment method string to enum
    payment_method_map = {
        "GCash": models.PaymentMethod.GCash,
        "Maya": models.PaymentMethod.Maya,
        "COD": models.PaymentMethod.COD,
        "Card": models.PaymentMethod.Card,
        "PayPal": models.PaymentMethod.PayPal,
        "Cash on Delivery": models.PaymentMethod.COD,
        "Credit/Debit Card": models.PaymentMethod.Card,
    }
    payment_method = payment_method_map.get(checkout_data.payment_method, models.PaymentMethod.COD)
    
    # Create the order
    new_order = models.Order(
        order_id=order_id,
        customer_id=customer.id,
        item_id=checkout_data.item_id,
        payment_method=payment_method,
        user_id=item.user_id,  # Assign to item owner (admin)
        status=models.OrderStatus.pending
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create payment record (shipping will be created when payment is marked as "Paid")
    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    payment = models.Payment(
        payment_id=payment_id,
        order_id=new_order.id,
        amount=float(item.price) * checkout_data.quantity,
        payment_method=checkout_data.payment_method,
        status=models.PaymentStatus.pending,
        user_id=item.user_id
    )
    db.add(payment)
    
    db.commit()
    
    return new_order

@router.get("/my-orders", response_model=List[schemas.OrderDetailResponse])
async def get_my_customer_orders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get orders where the current user is the customer"""
    print(f"\n📦 [MY-ORDERS] Current user: ID={current_user.id}, Email={current_user.email}")
    
    # Find ALL customer records for this user (they might have records under different admins)
    customers = db.query(models.Customer).filter(
        models.Customer.email == current_user.email
    ).all()
    
    print(f"📦 [MY-ORDERS] Found {len(customers)} customer records for email: {current_user.email}")
    
    if not customers:
        print(f"📦 [MY-ORDERS] No customer record found for email: {current_user.email}")
        return []
    
    # Get customer IDs
    customer_ids = [c.id for c in customers]
    print(f"📦 [MY-ORDERS] Customer IDs: {customer_ids}")
    
    # Get orders where this user is the customer (across all their customer records)
    orders = db.query(
        models.Order,
        models.Customer.name.label('customer_name'),
        models.Customer.address.label('customer_address'),
        models.Item.name.label('item_name'),
        models.Item.price.label('item_price'),
        models.Item.id.label('item_db_id'),
        models.Item.image_url.label('item_image_url')
    ).join(
        models.Customer, models.Order.customer_id == models.Customer.id
    ).join(
        models.Item, models.Order.item_id == models.Item.id
    ).filter(
        models.Order.customer_id.in_(customer_ids)
    ).all()
    
    print(f"📦 [MY-ORDERS] Found {len(orders)} orders for customer IDs {customer_ids}")
    for o in orders:
        print(f"   - Order: {o.Order.order_id}, Status: {o.Order.status}")
    
    # Get payments to find quantity
    result = []
    for order in orders:
        # Try to find payment for this order to get quantity and amount
        payment = db.query(models.Payment).filter(
            models.Payment.order_id == order.Order.id
        ).first()
        
        quantity = 1
        total_amount = float(order.item_price)
        
        if payment:
            # If payment exists, use its amount
            total_amount = float(payment.amount)
            # Try to infer quantity from amount/price
            if order.item_price > 0:
                quantity = int(total_amount / float(order.item_price))
        
        result.append({
            "id": order.Order.id,
            "order_id": order.Order.order_id,
            "customer_name": order.customer_name,
            "item_name": order.item_name,
            "item_id": order.item_db_id,
            "image_url": order.item_image_url,
            "customer_address": order.customer_address or "N/A",
            "payment_method": order.Order.payment_method.value if hasattr(order.Order.payment_method, 'value') else str(order.Order.payment_method),
            "status": order.Order.status.value if hasattr(order.Order.status, 'value') else str(order.Order.status),
            "created_at": order.Order.created_at,
            "item_price": float(order.item_price),
            "quantity": quantity,
            "total_amount": total_amount
        })
    
    print(f"📦 [MY-ORDERS] Returning {len(result)} order results")
    return result


@router.put("/my-orders/{order_id}")
async def update_my_order(
    order_id: int,
    order_data: schemas.OrderUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an order that belongs to the current user (customer).
    Customers can only mark shipped orders as completed/received.
    """
    # Find ALL customer records for this user
    customers = db.query(models.Customer).filter(
        models.Customer.email == current_user.email
    ).all()
    
    if not customers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer_ids = [c.id for c in customers]
    
    # Find the order that belongs to any of this user's customer records
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.customer_id.in_(customer_ids)
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Customers can only mark shipped orders as completed
    if order_data.status:
        new_status = order_data.status.lower()
        if new_status in ['completed', 'delivered']:
            if order.status != models.OrderStatus.shipped:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only shipped orders can be marked as completed"
                )
            order.status = models.OrderStatus.completed
            print(f"📦 [MY-ORDER-UPDATE] Order {order.order_id} marked as completed")
            
            # Also update payment status to 'paid' for this order
            payment = db.query(models.Payment).filter(
                models.Payment.order_id == order.id
            ).first()
            
            if payment:
                payment.status = models.PaymentStatus.paid
                print(f"💳 [MY-ORDER-UPDATE] Payment {payment.payment_id} marked as paid")
            
            # Also update shipping status to 'delivered' for this order
            shipping = db.query(models.Shipping).filter(
                models.Shipping.order_id == order.id
            ).first()
            
            if shipping:
                shipping.status = models.ShippingStatus.delivered
                print(f"🚚 [MY-ORDER-UPDATE] Shipping {shipping.shipping_id} marked as delivered")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customers can only mark orders as completed"
            )
    
    db.commit()
    db.refresh(order)
    
    return {
        "id": order.id,
        "order_id": order.order_id,
        "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
        "message": "Order marked as completed"
    }


@router.delete("/my-orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_my_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel/delete an order that belongs to the current user (customer).
    Only pending orders can be cancelled.
    """
    # Find ALL customer records for this user
    customers = db.query(models.Customer).filter(
        models.Customer.email == current_user.email
    ).all()
    
    if not customers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer_ids = [c.id for c in customers]
    
    # Find the order that belongs to any of this user's customer records
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.customer_id.in_(customer_ids)
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Only allow cancellation of pending orders
    if order.status not in [models.OrderStatus.pending, models.OrderStatus.new]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled"
        )
    
    # Delete associated payment record first
    payment = db.query(models.Payment).filter(
        models.Payment.order_id == order.id
    ).first()
    if payment:
        db.delete(payment)
    
    # Delete the order
    db.delete(order)
    db.commit()
    
    return None


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
        models.Item.name.label('item_name'),
        models.Item.price.label('item_price')
    ).join(
        models.Customer, models.Order.customer_id == models.Customer.id
    ).join(
        models.Item, models.Order.item_id == models.Item.id
    ).filter(
        models.Order.user_id == current_user.id
    ).all()
    
    # Get payments to find quantity
    result = []
    for order in orders:
        # Try to find payment for this order to get quantity and amount
        payment = db.query(models.Payment).filter(
            models.Payment.order_id == order.Order.id
        ).first()
        
        quantity = 1
        total_amount = float(order.item_price)
        
        if payment:
            # If payment exists, use its amount
            total_amount = float(payment.amount)
            # Try to infer quantity from amount/price
            if order.item_price > 0:
                quantity = int(total_amount / float(order.item_price))
        
        result.append({
            "id": order.Order.id,
            "order_id": order.Order.order_id,
            "customer_name": order.customer_name,
            "item_name": order.item_name,
            "customer_address": order.customer_address or "N/A",
            "payment_method": order.Order.payment_method.value if hasattr(order.Order.payment_method, 'value') else str(order.Order.payment_method),
            "status": order.Order.status.value if hasattr(order.Order.status, 'value') else str(order.Order.status),
            "created_at": order.Order.created_at,
            "item_price": float(order.item_price),
            "quantity": quantity,
            "total_amount": total_amount
        })
    
    return result

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
    print(f"\n📦 [UPDATE-ORDER] Order ID: {order_id}, User: {current_user.email}")
    print(f"📦 [UPDATE-ORDER] Update data: {order_data.dict(exclude_unset=True)}")
    
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    print(f"📦 [UPDATE-ORDER] Found order: {order.order_id}, current status: {order.status}")
    
    # Check if we're updating to shipped status
    new_status = order_data.dict(exclude_unset=True).get('status')
    is_setting_shipped = new_status and new_status.lower() == 'shipped'
    
    # Update only provided fields with proper enum conversion
    for field, value in order_data.dict(exclude_unset=True).items():
        if field == 'status' and value:
            # Convert string to OrderStatus enum
            status_value = value.lower()
            try:
                order.status = models.OrderStatus(status_value)
                print(f"📦 [UPDATE-ORDER] Set status to enum: {order.status}")
            except ValueError:
                print(f"📦 [UPDATE-ORDER] Invalid status value: {status_value}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status value: {status_value}"
                )
        else:
            setattr(order, field, value)
    
    # If setting to shipped, create shipping record if it doesn't exist
    if is_setting_shipped:
        print(f"📦 [UPDATE-ORDER] Order marked as shipped, checking for shipping record...")
        
        # Check if shipping record already exists for this order
        existing_shipping = db.query(models.Shipping).filter(
            models.Shipping.order_id == order.id
        ).first()
        
        if not existing_shipping:
            # Get customer address
            customer = db.query(models.Customer).filter(
                models.Customer.id == order.customer_id
            ).first()
            
            address = customer.address if customer and customer.address else "Address not provided"
            
            # Generate shipping ID
            shipping_id = f"SHP-{uuid.uuid4().hex[:8].upper()}"
            
            new_shipping = models.Shipping(
                shipping_id=shipping_id,
                order_id=order.id,
                courier="Standard Courier",  # Default courier
                address=address,
                status=models.ShippingStatus.shipped,
                user_id=current_user.id
            )
            db.add(new_shipping)
            print(f"📦 [UPDATE-ORDER] Created shipping record: {shipping_id}")
        else:
            # Update existing shipping to shipped
            existing_shipping.status = models.ShippingStatus.shipped
            print(f"📦 [UPDATE-ORDER] Updated existing shipping {existing_shipping.shipping_id} to shipped")
    
    # If setting to completed, also update payment to paid and shipping to delivered
    is_setting_completed = new_status and new_status.lower() == 'completed'
    if is_setting_completed:
        print(f"📦 [UPDATE-ORDER] Order marked as completed, updating payment and shipping...")
        
        # Update payment to paid
        payment = db.query(models.Payment).filter(
            models.Payment.order_id == order.id
        ).first()
        
        if payment:
            payment.status = models.PaymentStatus.paid
            print(f"📦 [UPDATE-ORDER] Payment {payment.payment_id} status updated to paid")
        
        # Update shipping to delivered
        shipping = db.query(models.Shipping).filter(
            models.Shipping.order_id == order.id
        ).first()
        
        if shipping:
            shipping.status = models.ShippingStatus.delivered
            print(f"📦 [UPDATE-ORDER] Shipping {shipping.shipping_id} status updated to delivered")
    
    db.commit()
    db.refresh(order)
    
    print(f"📦 [UPDATE-ORDER] Order updated successfully, new status: {order.status}")
    
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
