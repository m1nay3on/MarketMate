"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# Auth Schemas
class UserSignup(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    shop_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Customer Schemas
class CustomerCreate(BaseModel):
    customer_id: str
    name: str
    email: str
    address: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = "active"

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    customer_id: str
    name: str
    email: str
    address: Optional[str]
    phone: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Item Schemas
class ItemVariantCreate(BaseModel):
    variant_name: str

class ItemCreate(BaseModel):
    item_id: str
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    variants: Optional[List[str]] = []

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    item_id: str
    name: str
    description: Optional[str]
    price: Decimal
    image_url: Optional[str]
    rating: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderCreate(BaseModel):
    order_id: str
    customer_id: int
    item_id: int
    payment_method: str

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_id: str
    customer_id: int
    item_id: int
    payment_method: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    order_id: str
    customer_name: str
    item_name: str
    customer_address: str
    payment_method: str
    status: str
    created_at: datetime

# Shipping Schemas
class ShippingCreate(BaseModel):
    shipping_id: str
    order_id: int
    courier: str
    address: str

class ShippingUpdate(BaseModel):
    status: Optional[str] = None
    courier: Optional[str] = None
    address: Optional[str] = None

class ShippingResponse(BaseModel):
    id: int
    shipping_id: str
    order_id: int
    courier: str
    address: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Payment Schemas
class PaymentCreate(BaseModel):
    payment_id: str
    order_id: int
    amount: Decimal
    payment_method: str

class PaymentUpdate(BaseModel):
    status: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    payment_id: str
    order_id: int
    amount: Decimal
    payment_method: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentDetailResponse(BaseModel):
    id: int
    payment_id: str
    order_id: str
    customer_name: str
    email: str
    payment_method: str
    status: str
    amount: Decimal

# Review Schemas
class ReviewCreate(BaseModel):
    item_id: int
    customer_name: str
    rating: Decimal = Field(..., ge=0, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    item_id: int
    customer_name: str
    rating: Decimal
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReviewDetailResponse(BaseModel):
    id: int
    item_name: str
    customer_name: str
    rating: Decimal
    comment: Optional[str]
    created_at: datetime

# Reward Schemas
class RewardCreate(BaseModel):
    reward_id: str
    type: str
    code: str
    discount: Decimal
    validity_period: date

class RewardUpdate(BaseModel):
    type: Optional[str] = None
    discount: Optional[Decimal] = None
    validity_period: Optional[date] = None
    status: Optional[str] = None

class RewardResponse(BaseModel):
    id: int
    reward_id: str
    type: str
    code: str
    discount: Decimal
    validity_period: datetime
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_orders: int
    active_orders: int
    to_ship: int
    total_revenue: Decimal
    total_customers: int
    total_items: int
