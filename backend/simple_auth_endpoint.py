#!/usr/bin/env python3
"""Simple authentication bypass for testing"""

import sqlite3
import hashlib
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from app.core.config import settings

# Simple router for testing
router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

def get_simple_user(email: str, password: str):
    """Get user from simple SQLite table"""
    conn = sqlite3.connect('valuadis.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT id, email, full_name, password_hash, is_admin, is_valuer, is_active
        FROM users WHERE email = ? AND is_active = 1
        ''', (email,))
        
        user = cursor.fetchone()
        if user:
            # Verify password (simple check for testing)
            from app.core.security import verify_password
            if verify_password(password, user[3]):
                return {
                    'id': user[0],
                    'email': user[1],
                    'full_name': user[2],
                    'is_admin': bool(user[4]),
                    'is_valuer': bool(user[5]),
                    'is_active': bool(user[6])
                }
        return None
    finally:
        conn.close()

@router.post("/simple-login", response_model=TokenResponse, tags=["Authentication"])
async def simple_login(credentials: UserLogin):
    """Simple login bypass"""
    user = get_simple_user(credentials.email, credentials.password)
    
    if not user:
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

@router.get("/simple-me")
async def simple_get_current_user():
    """Simple current user endpoint"""
    return {"message": "Simple auth endpoint working"}

if __name__ == "__main__":
    # Test the simple auth
    login_data = {"email": "admin@valuadis.com", "password": "admin123"}
    print("Testing simple authentication...")
    user = get_simple_user(login_data["email"], login_data["password"])
    if user:
        print(f"✅ User found: {user}")
    else:
        print("❌ User not found or password incorrect")
