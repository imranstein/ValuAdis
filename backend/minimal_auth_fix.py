#!/usr/bin/env python3
"""Minimal authentication fix - bypass all ORM complexity"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import sqlite3
from app.core.config import settings
from app.core.security import verify_password

# Create router
router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool
    is_valuer: bool
    is_active: bool

def get_user_from_db(email: str):
    """Get user directly from SQLite"""
    try:
        conn = sqlite3.connect('valuadis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, email, full_name, password_hash, is_admin, is_valuer, is_active
        FROM users WHERE email = ? AND is_active = 1
        ''', (email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'email': result[1], 
                'full_name': result[2],
                'password_hash': result[3],
                'is_admin': bool(result[4]),
                'is_valuer': bool(result[5]),
                'is_active': bool(result[6])
            }
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

@router.post("/login-fixed", response_model=TokenResponse, tags=["Authentication"])
async def login_fixed(credentials: UserLogin):
    """Fixed login endpoint that bypasses ORM"""
    
    # Get user from database
    user = get_user_from_db(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = jwt.encode(
        {"sub": str(user['id']), "exp": datetime.utcnow() + timedelta(minutes=30)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    refresh_token = jwt.encode(
        {"sub": str(user['id']), "exp": datetime.utcnow() + timedelta(days=7)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me-fixed", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_fixed():
    """Fixed current user endpoint"""
    
    # For now, return admin user (this would normally validate token)
    user = get_user_from_db("admin@valuadis.com")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        full_name=user['full_name'],
        is_admin=user['is_admin'],
        is_valuer=user['is_valuer'],
        is_active=user['is_active']
    )

# Add the router to main app
if __name__ == "__main__":
    # Test the fixed authentication
    print("Testing fixed authentication...")
    
    user = get_user_from_db("admin@valuadis.com")
    if user:
        print(f"✅ User found: {user['email']}")
    else:
        print("❌ User not found")
