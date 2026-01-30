"""
Migration script to add role column to users table
"""
from sqlalchemy import create_engine, text
from backend.config import settings

def add_role_column():
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    
    try:
        # Check if role column already exists
        result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'role'"))
        if result.fetchone():
            print("Role column already exists!")
        else:
            # Add role column
            conn.execute(text("ALTER TABLE users ADD COLUMN role ENUM('admin', 'user') DEFAULT 'user' AFTER password_hash"))
            print("Role column added!")
        
        # Update admin user to have admin role
        conn.execute(text("UPDATE users SET role = 'admin' WHERE username = 'admin'"))
        conn.commit()
        print("Admin user role updated!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_role_column()
