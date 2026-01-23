"""
Database initialization and seeding script
Run this after creating the database schema
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal

# Add backend to path
sys.path.insert(0, '.')

from backend.config import settings
from backend.models.models import Base, User, Customer, Item, Order, Shipping, Payment, Review, Reward
from backend.utils.auth_utils import get_password_hash

# Create engine and session
engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin",
                email="admin@marketmate.com",
                password_hash=get_password_hash("admin123"),
                shop_name="MarketMate Store"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✓ Admin user created (ID: {admin.id})")
        else:
            print(f"✓ Admin user already exists (ID: {admin.id})")
        
        # Create sample customers
        print("\nCreating sample customers...")
        customers_data = [
            {"customer_id": "CUST001", "name": "Juan Dela Cruz", "email": "juan@example.com", "address": "Manila, PH", "phone": "555-0101"},
            {"customer_id": "CUST002", "name": "Maria Clara", "email": "maria@example.com", "address": "Quezon City, PH", "phone": "555-0102"},
            {"customer_id": "CUST003", "name": "Jose Rizal", "email": "jose@example.com", "address": "Calamba, PH", "phone": "555-0103"},
        ]
        
        for cust_data in customers_data:
            existing = db.query(Customer).filter(Customer.customer_id == cust_data["customer_id"]).first()
            if not existing:
                customer = Customer(**cust_data, user_id=admin.id)
                db.add(customer)
        db.commit()
        print(f"✓ Sample customers created")
        
        # Create sample items
        print("\nCreating sample items...")
        items_data = [
            {"item_id": "ITEM001", "name": "iPhone 17 Pro Max", "description": "Latest flagship smartphone", "price": Decimal("78000.00"), "rating": Decimal("4.9")},
            {"item_id": "ITEM002", "name": "Samsung Galaxy S25", "description": "Premium Android phone", "price": Decimal("65000.00"), "rating": Decimal("4.7")},
            {"item_id": "ITEM003", "name": "MacBook Pro M4", "description": "Professional laptop", "price": Decimal("120000.00"), "rating": Decimal("4.8")},
        ]
        
        for item_data in items_data:
            existing = db.query(Item).filter(Item.item_id == item_data["item_id"]).first()
            if not existing:
                item = Item(**item_data, user_id=admin.id, image_url="../images/iphonee.jpg")
                db.add(item)
        db.commit()
        print(f"✓ Sample items created")
        
        # Create sample orders
        print("\nCreating sample orders...")
        customers = db.query(Customer).filter(Customer.user_id == admin.id).all()
        items = db.query(Item).filter(Item.user_id == admin.id).all()
        
        if customers and items:
            orders_data = [
                {"order_id": "#1001", "customer_id": customers[0].id, "item_id": items[0].id, "payment_method": "GCash", "status": "shipped"},
                {"order_id": "#1002", "customer_id": customers[1].id, "item_id": items[1].id, "payment_method": "COD", "status": "pending"},
                {"order_id": "#1003", "customer_id": customers[2].id, "item_id": items[2].id, "payment_method": "Card", "status": "shipped"},
            ]
            
            for order_data in orders_data:
                existing = db.query(Order).filter(Order.order_id == order_data["order_id"]).first()
                if not existing:
                    order = Order(**order_data, user_id=admin.id)
                    db.add(order)
                    db.commit()
                    db.refresh(order)
                    
                    # Create shipping record
                    shipping = Shipping(
                        shipping_id=f"SH{order.id:03d}",
                        order_id=order.id,
                        courier="J&T Express",
                        address=customers[orders_data.index(order_data)].address,
                        status="shipped" if order.status == "shipped" else "preparing",
                        user_id=admin.id
                    )
                    db.add(shipping)
                    
                    # Create payment record
                    payment = Payment(
                        payment_id=f"PAY{order.id:04d}",
                        order_id=order.id,
                        amount=Decimal("1000.00"),
                        payment_method=order.payment_method,
                        status="paid" if order.status == "shipped" else "pending",
                        user_id=admin.id
                    )
                    db.add(payment)
            
            db.commit()
            print(f"✓ Sample orders, shipping, and payments created")
        
        # Create sample reviews
        print("\nCreating sample reviews...")
        if items:
            reviews_data = [
                {"item_id": items[0].id, "customer_name": "Happy Customer", "rating": Decimal("4.9"), "comment": "Excellent product! Highly recommended."},
                {"item_id": items[0].id, "customer_name": "Tech Reviewer", "rating": Decimal("4.8"), "comment": "Great features and performance."},
                {"item_id": items[1].id, "customer_name": "Android Fan", "rating": Decimal("4.7"), "comment": "Best Android phone in the market."},
            ]
            
            for review_data in reviews_data:
                review = Review(**review_data, user_id=admin.id)
                db.add(review)
            db.commit()
            print(f"✓ Sample reviews created")
        
        # Create sample rewards
        print("\nCreating sample rewards...")
        rewards_data = [
            {"reward_id": "REW001", "type": "Voucher", "code": "WELCOME20", "discount": Decimal("20.00"), "validity_period": datetime.now() + timedelta(days=30)},
            {"reward_id": "REW002", "type": "Discount", "code": "SAVE10", "discount": Decimal("10.00"), "validity_period": datetime.now() + timedelta(days=60)},
        ]
        
        for reward_data in rewards_data:
            existing = db.query(Reward).filter(Reward.code == reward_data["code"]).first()
            if not existing:
                reward = Reward(**reward_data, user_id=admin.id)
                db.add(reward)
        db.commit()
        print(f"✓ Sample rewards created")
        
        print("\n" + "="*50)
        print("✓ Database seeding completed successfully!")
        print("="*50)
        print("\nYou can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nStart the server with:")
        print("  uvicorn backend.main:app --reload")
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("="*50)
    print("  MarketMate Database Seeding")
    print("="*50)
    print(f"Database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}")
    print("="*50)
    print()
    
    seed_database()
