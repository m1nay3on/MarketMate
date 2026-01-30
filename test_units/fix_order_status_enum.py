"""Fix the orders.status enum in MySQL to include 'paid' status."""
from backend.database.connection import engine
from sqlalchemy import text

def fix_enum():
    with engine.connect() as conn:
        # Add 'paid' to the orders status enum
        sql = """
        ALTER TABLE orders 
        MODIFY COLUMN status ENUM('pending', 'paid', 'shipped', 'delivered', 'completed', 'cancelled', 'new') 
        NOT NULL DEFAULT 'pending'
        """
        conn.execute(text(sql))
        conn.commit()
        print("✅ Database updated: orders.status now includes 'paid' status!")

if __name__ == "__main__":
    fix_enum()
