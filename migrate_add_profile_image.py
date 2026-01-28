"""
Migration script to add profile_image column to User table
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'profile_image' not in columns:
        print("Adding profile_image column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN profile_image VARCHAR(200)")
        conn.commit()
        print("✓ Column added successfully!")
    else:
        print("profile_image column already exists.")
    
    conn.close()
else:
    print("Database not found. It will be created when you run the app.")
