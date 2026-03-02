"""
User Repository

Data access layer for user operations
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.data.repositories.base import BaseRepository
from app.data.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        return self.db.query(User).filter(User.phone == phone).first()
    
    def get_by_license(self, license_number: str) -> Optional[User]:
        """Get user by license number"""
        return self.db.query(User).filter(User.license_number == license_number).first()
    
    def create_user(self, user_data: dict) -> User:
        """Create new user"""
        return self.create(user_data)
    
    def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update user information"""
        user = self.get(user_id)
        if user:
            return self.update(user, update_data)
        return None
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get(user_id)
        if user:
            return self.update(user, {"is_active": False})
        return False
