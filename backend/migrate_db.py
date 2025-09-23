#!/usr/bin/env python3
"""
Database migration script to add new columns to existing tables.
Run this script to update your database schema.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new columns to the User table"""
    
    # Get the database path
    instance_dir = Path(__file__).parent / 'instance'
    instance_dir.mkdir(exist_ok=True)
    db_path = instance_dir / 'app.db'
    
    if not db_path.exists():
        print("Database file not found. Please run the main app first to create the database.")
        return
    
    print(f"Migrating database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add notification_preferences column if it doesn't exist
        if 'notification_preferences' not in columns:
            print("Adding notification_preferences column...")
            cursor.execute("ALTER TABLE user ADD COLUMN notification_preferences TEXT")
            print("✓ notification_preferences column added")
        else:
            print("✓ notification_preferences column already exists")
        
        # Add privacy_preferences column if it doesn't exist
        if 'privacy_preferences' not in columns:
            print("Adding privacy_preferences column...")
            cursor.execute("ALTER TABLE user ADD COLUMN privacy_preferences TEXT")
            print("✓ privacy_preferences column added")
        else:
            print("✓ privacy_preferences column already exists")
        
        # Commit the changes
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
