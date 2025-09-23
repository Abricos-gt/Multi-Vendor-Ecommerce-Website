#!/usr/bin/env python3
"""
Add database indexes for better performance.
Run this script to optimize database queries.
"""

import sqlite3
import os
from pathlib import Path

def add_indexes():
    """Add indexes to improve database performance"""
    
    # Get the database path
    instance_dir = Path(__file__).parent / 'instance'
    instance_dir.mkdir(exist_ok=True)
    db_path = instance_dir / 'app.db'
    
    if not db_path.exists():
        print("Database file not found. Please run the main app first to create the database.")
        return
    
    print(f"Adding indexes to database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Indexes for Product table
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_product_category ON product(category)",
            "CREATE INDEX IF NOT EXISTS idx_product_vendor_id ON product(vendor_id)",
            "CREATE INDEX IF NOT EXISTS idx_product_created_at ON product(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_product_price ON product(price)",
            "CREATE INDEX IF NOT EXISTS idx_product_category_created ON product(category, created_at)",
            
            # Indexes for User table
            "CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON user(role)",
            
            # Indexes for Order table
            "CREATE INDEX IF NOT EXISTS idx_order_user_id ON \"order\"(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_order_status ON \"order\"(status)",
            "CREATE INDEX IF NOT EXISTS idx_order_created_at ON \"order\"(created_at)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✓ Created index: {index_sql.split('idx_')[1].split(' ON')[0]}")
            except sqlite3.Error as e:
                print(f"❌ Failed to create index: {e}")
        
        # Commit the changes
        conn.commit()
        print("\n🎉 Database indexes added successfully!")
        
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_indexes()
