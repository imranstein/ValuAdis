"""
Base Repository

Generic repository pattern for ValuAdis data access layer
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filters"""
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def get_multi_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records for a specific user with pagination"""
        # Check if model has user_id field and fail fast if not
        if not hasattr(self.model, 'user_id'):
            raise AttributeError(f"Model {self.model.__name__} does not have user_id attribute")
        
        query = self.db.query(self.model).filter(self.model.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update existing record"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete record by ID"""
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with filters"""
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if record exists with given filters"""
        return self.count(filters) > 0
