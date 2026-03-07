"""
Authentication Service

Business logic for user authentication and authorization
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import AuthenticationException, ValidationException
from app.data.repositories.user_repository import UserRepository
from app.data.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
    
    async def create_user(self, user_data: dict) -> User:
        """Create new user with validation"""
        # Check if email already exists
        if self.user_repo.get_by_email(user_data["email"]):
            raise ValidationException("Email already registered")
        
        # Check if phone already exists
        if self.user_repo.get_by_phone(user_data["phone"]):
            raise ValidationException("Phone number already registered")
        
        # Check if license number already exists
        if self.user_repo.get_by_license(user_data["license_number"]):
            raise ValidationException("License number already registered")
        
        # Hash password
        user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        user_data["is_approved"] = False  # VA-118: New registrations require admin approval
        return self.user_repo.create_user(user_data)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.user_repo.get_by_email(email)
        
        if not user:
            raise AuthenticationException("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")
        if not getattr(user, "is_approved", True):
            raise AuthenticationException("Account pending approval. Please contact an administrator.")
        if not verify_password(password, user.password_hash):
            raise AuthenticationException("Invalid email or password")
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.user_repo.get(user_id)
    
    async def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update user information"""
        # Don't allow password update through this method
        if "password" in update_data:
            del update_data["password"]
        
        # Check if email is being updated and already exists
        if "email" in update_data:
            existing_user = self.user_repo.get_by_email(update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValidationException("Email already registered")
        
        # Check if phone is being updated and already exists
        if "phone" in update_data:
            existing_user = self.user_repo.get_by_phone(update_data["phone"])
            if existing_user and existing_user.id != user_id:
                raise ValidationException("Phone number already registered")
        
        return self.user_repo.update_user(user_id, update_data)
