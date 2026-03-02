from sqlalchemy.orm import Session
from app.data.repositories.base import BaseRepository
from app.data.models.valuation import Valuation

class ValuationRepository(BaseRepository[Valuation]):
    """Repository for Valuation operations"""
    
    def __init__(self, db: Session):
        super().__init__(Valuation, db)
    
    def get_user_valuations(self, user_id: int, skip: int = 0, limit: int = 100):
        """Get all valuations for a specific user"""
        return self.get_multi_by_user(user_id=user_id, skip=skip, limit=limit)
    
    def get_valuation_by_id_and_user(self, valuation_id: int, user_id: int):
        """Get a specific valuation by ID, ensuring it belongs to user"""
        return self.db.query(Valuation).filter(Valuation.id == valuation_id, Valuation.user_id == user_id).first()
