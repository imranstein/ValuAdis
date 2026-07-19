"""
Property Photo Model

Server-stored property photos (citizen + staff upload). Filenames are
server-generated (uuid hex), never derived from client input, so nothing
about the original upload leaks through the stored path. Public visibility
(a property behind a PUBLISHED rental listing) is resolved by the property
module's routes, not by this model.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PropertyPhoto(Base):
    __tablename__ = "property_photos"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Server-generated (uuid4 hex + extension); never the client's filename.
    filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    byte_size = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    property = relationship("Property", back_populates="photos")

    def __repr__(self):
        return f"<PropertyPhoto(id={self.id}, property_id={self.property_id}, position={self.position})>"
