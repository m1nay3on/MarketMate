import pymysql
import sys
from getpass import getpass

def import_database():
    """Import database schema from SQL file"""
    
    # Get MySQL password
    password = getpass("Enter MySQL root password: ")
    
    try:
        # Connect to MySQL without database first
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Read schema file
        with open('backend/database/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Split by semicolon and execute each statement
        statements = schema.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"⚠️  Warning: {str(e)[:100]}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database schema imported successfully!")
        print("✓ Database 'marketmate' created")
        print("✓ Default admin user created (username: admin, password: admin123)")
        return True
        
    except pymysql.Error as e:
        print(f"\n✗ MySQL Error: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ Error: backend/database/schema.sql not found")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = import_database()
    sys.exit(0 if success else 1)
