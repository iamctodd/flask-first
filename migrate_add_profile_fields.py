"""
Migration script to add profile fields to User table
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add missing columns
    new_columns = {
        'first_name': 'VARCHAR(100)',
        'last_name': 'VARCHAR(100)',
        'display_name': 'VARCHAR(100)',
        'city': 'VARCHAR(100)',
        'state': 'VARCHAR(100)',
        'country': 'VARCHAR(100)',
        'profile_image': 'VARCHAR(200)'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            print(f"Adding {col_name} column to user table...")
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            conn.commit()
            print(f"✓ {col_name} column added successfully!")
        else:
            print(f"{col_name} column already exists.")
    
    conn.close()
else:
    print("Database not found. It will be created when you run the app.")