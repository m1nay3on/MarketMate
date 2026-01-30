"""
Database migration script to fix missing columns and update enums
Run this script to update the database schema to match the models
"""
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymysql
from backend.config import settings

def fix_database():
    """Fix database schema issues"""
    print("=" * 50)
    print("   MarketMate Database Migration")
    print("=" * 50)
    
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        print("\n🔍 Checking and fixing database schema...\n")
        
        # 1. Check if orders.status column exists
        print("1. Checking orders table...")
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'status'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            print("   ➕ Adding 'status' column to orders table...")
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN status ENUM('pending', 'shipped', 'cancelled', 'new') DEFAULT 'pending' 
                AFTER payment_method
            """)
            print("   ✅ Added 'status' column to orders table")
        else:
            print("   ✅ 'status' column already exists in orders table")
        
        # 2. Update payment_method enum to include Maya
        print("\n2. Checking payment_method enum...")
        cursor.execute("""
            SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'payment_method'
        """, (settings.DB_NAME,))
        
        result = cursor.fetchone()
        if result and 'Maya' not in result[0]:
            print("   ➕ Updating payment_method enum to include 'Maya'...")
            cursor.execute("""
                ALTER TABLE orders 
                MODIFY COLUMN payment_method ENUM('GCash', 'Maya', 'COD', 'Card', 'PayPal') NOT NULL
            """)
            print("   ✅ Updated payment_method enum")
        else:
            print("   ✅ payment_method enum already includes 'Maya'")
        
        # 3. Check if orders.updated_at column exists
        print("\n3. Checking orders.updated_at column...")
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'updated_at'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            print("   ➕ Adding 'updated_at' column to orders table...")
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            """)
            print("   ✅ Added 'updated_at' column to orders table")
        else:
            print("   ✅ 'updated_at' column already exists")
        
        # 4. Check shipping table columns
        print("\n4. Checking shipping table...")
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'shipping' AND COLUMN_NAME = 'shipping_id'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            print("   ➕ Adding 'shipping_id' column to shipping table...")
            cursor.execute("""
                ALTER TABLE shipping 
                ADD COLUMN shipping_id VARCHAR(20) UNIQUE NOT NULL FIRST
            """)
            # Generate shipping_ids for existing records
            cursor.execute("UPDATE shipping SET shipping_id = CONCAT('SHP-', LPAD(id, 8, '0')) WHERE shipping_id IS NULL OR shipping_id = ''")
            print("   ✅ Added 'shipping_id' column to shipping table")
        else:
            print("   ✅ 'shipping_id' column already exists")
        
        # Check courier column
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'shipping' AND COLUMN_NAME = 'courier'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            print("   ➕ Adding 'courier' column to shipping table...")
            cursor.execute("""
                ALTER TABLE shipping 
                ADD COLUMN courier VARCHAR(100) NOT NULL DEFAULT 'Standard Shipping'
            """)
            print("   ✅ Added 'courier' column to shipping table")
        else:
            print("   ✅ 'courier' column already exists")
        
        # Check address column
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'shipping' AND COLUMN_NAME = 'address'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            print("   ➕ Adding 'address' column to shipping table...")
            cursor.execute("""
                ALTER TABLE shipping 
                ADD COLUMN address TEXT NOT NULL DEFAULT 'Address not provided'
            """)
            print("   ✅ Added 'address' column to shipping table")
        else:
            print("   ✅ 'address' column already exists")
        
        # 5. Check payments table
        print("\n5. Checking payments table...")
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'payments' AND COLUMN_NAME = 'payment_id'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            print("   ➕ Adding 'payment_id' column to payments table...")
            try:
                cursor.execute("""
                    ALTER TABLE payments 
                    ADD COLUMN payment_id VARCHAR(20) UNIQUE FIRST
                """)
                # Generate payment_ids for existing records
                cursor.execute("UPDATE payments SET payment_id = CONCAT('PAY-', LPAD(id, 8, '0')) WHERE payment_id IS NULL OR payment_id = ''")
                cursor.execute("ALTER TABLE payments MODIFY COLUMN payment_id VARCHAR(20) UNIQUE NOT NULL")
                print("   ✅ Added 'payment_id' column to payments table")
            except Exception as e:
                print(f"   ⚠️ Could not add payment_id: {e}")
        else:
            print("   ✅ 'payment_id' column already exists")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Database migration completed successfully!")
        print("=" * 50)
        print("\nYou can now restart the server.")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_database()
