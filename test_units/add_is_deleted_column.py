"""
Migration script to add is_deleted column to items table
Run this script to update existing database with the soft delete feature
"""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def add_is_deleted_column():
    """Add is_deleted column to items table if it doesn't exist"""
    try:
        # Get database credentials from environment
        host = os.getenv("DB_HOST", "127.0.0.1")
        if host == "localhost":
            host = "127.0.0.1"  # Use IP instead of hostname
        port = int(os.getenv("DB_PORT", "3306"))
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "marketmate_db")
        
        print(f"Connecting to MySQL at {host}:{port}...")
        
        # Connect to database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'items'
            AND COLUMN_NAME = 'is_deleted'
        """, (database,))
        
        exists = cursor.fetchone()[0] > 0
        
        if not exists:
            # Add the column
            print("Adding is_deleted column to items table...")
            cursor.execute("""
                ALTER TABLE items
                ADD COLUMN is_deleted TINYINT(1) DEFAULT 0
            """)
            conn.commit()
            print("✅ Column 'is_deleted' added successfully!")
        else:
            print("✅ Column 'is_deleted' already exists.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nNote: Make sure MySQL is running and the database exists.")
        print("If MySQL is not running, the column will be created automatically")
        print("when the application starts (SQLAlchemy will sync the model).")

if __name__ == "__main__":
    add_is_deleted_column()
