"""
SQLAlchemy models for MarketMate database
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.connection import Base
import enum

# Status Enums
class CustomerStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"           # User paid, waiting for admin to confirm/ship
    shipped = "shipped"     # Admin confirmed shipping
    delivered = "delivered" # Order delivered to customer
    completed = "completed" # Order completed
    cancelled = "cancelled"
    new = "new"

class PaymentMethod(str, enum.Enum):
    GCash = "GCash"
    Maya = "Maya"
    COD = "COD"
    Card = "Card"
    PayPal = "PayPal"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"

class ShippingStatus(str, enum.Enum):
    preparing = "preparing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class RewardStatus(str, enum.Enum):
    valid = "valid"
    expired = "expired"

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    shop_name = Column(String(100), default="My Shop")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customers = relationship("Customer", back_populates="user", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="user", cascade="all, delete-orphan")
    shipping = relationship("Shipping", back_populates="user", cascade="all, delete-orphan")


# Customer Model
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    status = Column(Enum(CustomerStatus), default=CustomerStatus.active)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="customers")
    orders = relationship("Order", back_populates="customer")


# Item Model
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(500))
    rating = Column(DECIMAL(2, 1), default=0.0)
    is_deleted = Column(Integer, default=0)  # Soft delete flag: 0=active, 1=deleted
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="items")
    variants = relationship("ItemVariant", back_populates="item", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="item")
    reviews = relationship("Review", back_populates="item")


# Item Variant Model
class ItemVariant(Base):
    __tablename__ = "item_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    variant_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("Item", back_populates="variants")


# Order Model
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    item = relationship("Item", back_populates="orders")
    shipping = relationship("Shipping", back_populates="order", uselist=False)
    payments = relationship("Payment", back_populates="order")


# Shipping Model
class Shipping(Base):
    __tablename__ = "shipping"
    
    id = Column(Integer, primary_key=True, index=True)
    shipping_id = Column(String(20), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    courier = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    status = Column(Enum(ShippingStatus), default=ShippingStatus.preparing)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="shipping")
    order = relationship("Order", back_populates="shipping")


# Payment Model
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(20), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payments")


# Review Model
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    rating = Column(DECIMAL(2, 1), nullable=False)
    comment = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    item = relationship("Item", back_populates="reviews")


# Reward Model
class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    reward_id = Column(String(20), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount = Column(DECIMAL(10, 2), nullable=False)
    validity_period = Column(DateTime, nullable=False)
    status = Column(Enum(RewardStatus), default=RewardStatus.valid)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="rewards")
