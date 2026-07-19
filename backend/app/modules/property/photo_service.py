"""
Property Photo Service

Real photo storage for properties (citizen + staff upload). Uploaded bytes
are re-validated server-side by decoding them as an image (Pillow reads the
actual file header/magic bytes, not the client-supplied content-type) before
anything touches disk. Files are written under a configurable media root
with server-generated names; nothing about the original filename or a
filesystem path is ever returned to a caller.
"""

import io
import os
import uuid
from typing import Dict, List, Optional

from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.data.models.property_photo import PropertyPhoto

# Constraints (plan: "max ~8 photos/property, max ~5MB each, jpeg/png/webp only").
MAX_PHOTOS_PER_PROPERTY = 8
MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

# Pillow's detected format -> (stored file extension, canonical content-type).
ALLOWED_PHOTO_FORMATS: Dict[str, tuple] = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}


def photo_url(property_id: int, photo_id: int) -> str:
    """Opaque public URL for a photo — no filesystem path, no filename."""
    return f"/api/v1/properties/{property_id}/photos/{photo_id}/file"


class PropertyPhotoService:
    def __init__(self, db: Session):
        self.db = db

    def upload(self, property_id: int, data: bytes, uploaded_by_user_id: int) -> PropertyPhoto:
        """Validate and store one photo. Caller (routes.py) has already
        confirmed the actor may write to this property and enforced the
        max-size limit while reading the multipart body."""
        if not data:
            raise ValidationException("Uploaded file is empty.")

        existing_count = (
            self.db.query(PropertyPhoto)
            .filter(PropertyPhoto.property_id == property_id)
            .count()
        )
        if existing_count >= MAX_PHOTOS_PER_PROPERTY:
            raise ValidationException(
                f"A property may have at most {MAX_PHOTOS_PER_PROPERTY} photos."
            )

        image_format = self._detect_image_format(data)
        if image_format is None:
            raise ValidationException("File is not a valid JPEG, PNG, or WEBP image.")

        extension, content_type = ALLOWED_PHOTO_FORMATS[image_format]
        filename = f"{uuid.uuid4().hex}.{extension}"
        directory = self._media_dir(property_id)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, filename), "wb") as fh:
            fh.write(data)

        photo = PropertyPhoto(
            property_id=property_id,
            filename=filename,
            content_type=content_type,
            byte_size=len(data),
            position=existing_count,
            uploaded_by_user_id=uploaded_by_user_id,
        )
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def list_for_property(self, property_id: int) -> List[PropertyPhoto]:
        return (
            self.db.query(PropertyPhoto)
            .filter(PropertyPhoto.property_id == property_id)
            .order_by(PropertyPhoto.position.asc(), PropertyPhoto.id.asc())
            .all()
        )

    def get_photo(self, property_id: int, photo_id: int) -> Optional[PropertyPhoto]:
        return (
            self.db.query(PropertyPhoto)
            .filter(PropertyPhoto.id == photo_id, PropertyPhoto.property_id == property_id)
            .first()
        )

    def file_path_for(self, photo: PropertyPhoto) -> str:
        return os.path.join(self._media_dir(photo.property_id), photo.filename)

    def delete(self, property_id: int, photo_id: int) -> bool:
        photo = self.get_photo(property_id, photo_id)
        if not photo:
            return False
        file_path = self.file_path_for(photo)
        self.db.delete(photo)
        self.db.commit()
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # DB row is already gone; disk cleanup is best-effort
        return True

    def _media_dir(self, property_id: int) -> str:
        return os.path.join(settings.MEDIA_ROOT, "property_photos", str(property_id))

    @staticmethod
    def _detect_image_format(data: bytes) -> Optional[str]:
        """Decode the actual bytes (Pillow reads the real header), not the
        client-supplied content-type or filename extension."""
        try:
            with Image.open(io.BytesIO(data)) as probe:
                probe.verify()
            with Image.open(io.BytesIO(data)) as reopened:
                fmt = reopened.format
        except (UnidentifiedImageError, OSError, ValueError):
            return None
        return fmt if fmt in ALLOWED_PHOTO_FORMATS else None
