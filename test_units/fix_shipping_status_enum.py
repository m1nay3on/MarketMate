"""
Script to update the shipping.status ENUM column to include 'delivered' value.
Run this script to fix the MySQL enum for shipping status.
"""
import pymysql

def update_shipping_status_enum():
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host='localhost',
            database='marketmate_db',
            user='root',
            password='marketmate_password_2026',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            cursor = connection.cursor()
            
            print("Connected to MySQL database")
            print("Updating shipping.status ENUM to include 'delivered'...")
            
            # Update the ENUM column to include 'delivered'
            alter_query = """
                ALTER TABLE shipping 
                MODIFY COLUMN status ENUM('preparing', 'shipped', 'delivered', 'cancelled') 
                DEFAULT 'preparing'
            """
            
            cursor.execute(alter_query)
            connection.commit()
            
            print("✓ Successfully updated shipping.status ENUM!")
            print("  New values: 'preparing', 'shipped', 'delivered', 'cancelled'")
            
            # Verify the change
            cursor.execute("SHOW COLUMNS FROM shipping LIKE 'status'")
            result = cursor.fetchone()
            if result:
                print(f"  Verified column type: {result['Type']}")
            
            print("\nDatabase connection closed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_shipping_status_enum()
