#!/usr/bin/env python3
"""Create admin user directly in SQLite"""

import sqlite3
from datetime import datetime
import hashlib

def hash_password(password: str) -> str:
    """Simple password hashing for testing"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin():
    """Create admin user in SQLite database"""
    try:
        conn = sqlite3.connect('valuadis.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_valuer INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            phone TEXT,
            municipality TEXT,
            license_number TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # Check if admin already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@valuadis.com',))
        existing = cursor.fetchone()
        
        if existing:
            print('✅ Admin user already exists')
            cursor.execute('SELECT full_name, is_admin FROM users WHERE email = ?', ('admin@valuadis.com',))
            admin = cursor.fetchone()
            print(f'   Name: {admin[0]}, Admin: {bool(admin[1])}')
        else:
            # Create admin user
            now = datetime.utcnow().isoformat()
            cursor.execute('''
            INSERT INTO users (
                email, full_name, password_hash, is_admin, is_valuer, 
                is_active, phone, municipality, license_number, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'admin@valuadis.com',
                'System Administrator',
                hash_password('Admin123!'),
                1,  # is_admin
                1,  # is_valuer
                1,  # is_active
                '+251911000000',
                'Addis Ababa',
                'ADMIN-001',
                now,
                now
            ))
            
            print('✅ Admin user created successfully')
            print('   Email: admin@valuadis.com')
            print('   Password: Admin123!')
            print('   Hash:', hash_password('Admin123!')[:20] + '...')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error creating admin user: {e}')

if __name__ == '__main__':
    create_admin()
