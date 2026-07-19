"""
Property Photo Tests

Real photo upload for citizen + staff: multipart upload (owner/staff only),
public-vs-scoped serving (public once the property backs a PUBLISHED rental
listing, owner/staff/officer-scoped otherwise), size/type/count limits, and
ordering.
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings
from app.modules.property.photo_service import MAX_PHOTO_SIZE_BYTES, MAX_PHOTOS_PER_PROPERTY

OWNER_SIGNUP = {
    "email": "photo-owner@example.com",
    "full_name": "Owner Photo",
    "phone": "+251911100001",
    "password": "Ownerpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "100000000001",
    "account_type": "property_owner",
}

OTHER_OWNER_SIGNUP = {
    "email": "photo-other-owner@example.com",
    "full_name": "Other Owner",
    "phone": "+251911100002",
    "password": "Ownerpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "100000000002",
    "account_type": "property_owner",
}

RENTER_SIGNUP = {
    "email": "photo-renter@example.com",
    "full_name": "Renter Photo",
    "phone": "+251911100003",
    "password": "Renterpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "100000000003",
    "account_type": "renter",
}

STAFF_REGISTER = {
    "email": "photo-staff@example.com",
    "full_name": "Staff Photo",
    "phone": "+251911100004",
    "password": "Staffpass1!",
    "municipality": "Addis Ababa",
    "license_number": "VAL-2026-PHOTO",
}

PROPERTY_PAYLOAD = {
    "address": "Bole, Addis Ababa",
    "municipality": "Addis Ababa",
    "subcity": "Bole",
    "property_type": "residential",
    "property_subtype": "apartment",
    "area_sqm": 120.0,
    "number_of_bedrooms": 2,
    "owner_name": "Owner Photo",
    "owner_phone": "+251911100001",
    "coordinates": [
        [38.7578, 9.0320],
        [38.7580, 9.0320],
        [38.7580, 9.0318],
        [38.7578, 9.0318],
        [38.7578, 9.0320],
    ],
}


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _signup(client: TestClient, payload: dict) -> str:
    response = client.post("/api/v1/rentals/signup", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]["access_token"]


def _register_staff(client: TestClient) -> str:
    response = client.post("/api/v1/auth/register", json=STAFF_REGISTER)
    assert response.status_code == 201, response.text
    body = response.json()
    return body.get("access_token") or body["data"]["access_token"]


def _create_property(client: TestClient, owner_token: str) -> int:
    response = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(owner_token))
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


def _valid_image_bytes(fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color=(120, 30, 30)).save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _isolated_media_root(tmp_path, monkeypatch):
    """Photos must not land in the repo's real media directory during tests."""
    monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))


@pytest.fixture
def owner_token(client):
    return _signup(client, OWNER_SIGNUP)


@pytest.fixture
def other_owner_token(client):
    return _signup(client, OTHER_OWNER_SIGNUP)


@pytest.fixture
def renter_token(client):
    return _signup(client, RENTER_SIGNUP)


@pytest.fixture
def staff_token(client):
    return _register_staff(client)


@pytest.fixture
def property_id(client, owner_token):
    return _create_property(client, owner_token)


class TestUploadAuthorization:
    def test_owner_can_upload(self, client, property_id, owner_token):
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        assert response.status_code == 201, response.text
        data = response.json()["data"]
        assert data["url"] == f"/api/v1/properties/{property_id}/photos/{data['id']}/file"
        assert data["position"] == 0

    def test_staff_can_upload_to_any_property(self, client, property_id, staff_token):
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(staff_token),
        )
        assert response.status_code == 201, response.text

    def test_other_owner_cannot_upload(self, client, property_id, other_owner_token):
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(other_owner_token),
        )
        assert response.status_code == 404  # scoped like every other property write

    def test_renter_cannot_upload(self, client, property_id, renter_token):
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(renter_token),
        )
        assert response.status_code == 403

    def test_upload_requires_authentication(self, client, property_id):
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
        )
        assert response.status_code == 401


class TestUploadValidation:
    def test_rejects_file_larger_than_max_size(self, client, property_id, owner_token):
        oversized = b"\xff" * (MAX_PHOTO_SIZE_BYTES + 1)
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("big.jpg", oversized, "image/jpeg")},
            headers=_headers(owner_token),
        )
        assert response.status_code == 413

    def test_rejects_non_image_content_disguised_as_jpeg(self, client, property_id, owner_token):
        """Content-type says image/jpeg but the bytes are plain text — magic
        byte re-validation must catch what content-type sniffing would miss."""
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("fake.jpg", b"not actually an image", "image/jpeg")},
            headers=_headers(owner_token),
        )
        assert response.status_code == 400
        assert "valid" in response.json()["detail"].lower()

    def test_accepts_webp(self, client, property_id, owner_token):
        response = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.webp", _valid_image_bytes("WEBP"), "image/webp")},
            headers=_headers(owner_token),
        )
        assert response.status_code == 201, response.text

    def test_rejects_ninth_photo(self, client, property_id, owner_token):
        for _ in range(MAX_PHOTOS_PER_PROPERTY):
            response = client.post(
                f"/api/v1/properties/{property_id}/photos",
                files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
                headers=_headers(owner_token),
            )
            assert response.status_code == 201, response.text

        ninth = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        assert ninth.status_code == 400
        assert str(MAX_PHOTOS_PER_PROPERTY) in ninth.json()["detail"]


class TestOrdering:
    def test_photos_list_in_upload_order(self, client, property_id, owner_token):
        uploaded_ids = []
        for _ in range(3):
            response = client.post(
                f"/api/v1/properties/{property_id}/photos",
                files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
                headers=_headers(owner_token),
            )
            uploaded_ids.append(response.json()["data"]["id"])

        listed = client.get(f"/api/v1/properties/{property_id}/photos", headers=_headers(owner_token))
        assert listed.status_code == 200
        listed_ids = [p["id"] for p in listed.json()["data"]]
        assert listed_ids == uploaded_ids
        assert [p["position"] for p in listed.json()["data"]] == [0, 1, 2]


class TestReadAuthorization:
    def test_owner_can_list_own_photos(self, client, property_id, owner_token):
        client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        response = client.get(f"/api/v1/properties/{property_id}/photos", headers=_headers(owner_token))
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_unpublished_property_photos_are_not_public(self, client, property_id, owner_token):
        client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        response = client.get(f"/api/v1/properties/{property_id}/photos")
        assert response.status_code == 401

    def test_other_owner_cannot_list_unpublished_photos(self, client, property_id, owner_token, other_owner_token):
        client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        response = client.get(f"/api/v1/properties/{property_id}/photos", headers=_headers(other_owner_token))
        assert response.status_code == 403

    def test_staff_can_list_any_property_photos(self, client, property_id, owner_token, staff_token):
        client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        response = client.get(f"/api/v1/properties/{property_id}/photos", headers=_headers(staff_token))
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_file_bytes_downloadable_by_owner(self, client, property_id, owner_token):
        upload = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        photo_id = upload.json()["data"]["id"]
        response = client.get(
            f"/api/v1/properties/{property_id}/photos/{photo_id}/file", headers=_headers(owner_token)
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0


class TestPublicListingVisibility:
    def _make_officer(self, client: TestClient, db_session) -> str:
        from app.data.models.role import Role
        from app.data.models.user import User

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "photo-officer@example.com",
                "full_name": "Officer Photo",
                "phone": "+251911100005",
                "password": "Officerpass1!",
                "municipality": "Addis Ababa",
                "license_number": "OFF-2026-PHOTO",
            },
        )
        token = response.json()["data"]["access_token"]
        user = db_session.query(User).filter(User.email == "photo-officer@example.com").first()
        role = db_session.query(Role).filter(Role.name == "rental_officer").first()
        if role is None:
            role = Role(name="rental_officer", display_name="Rental Officer", is_active=True)
            db_session.add(role)
            db_session.commit()
        user.roles.append(role)
        db_session.commit()
        return token

    def _publish(self, client, db_session, property_id, owner_token) -> str:
        from app.data.models.user import User

        listing = client.post(
            "/api/v1/rentals/listings", json={"property_id": property_id}, headers=_headers(owner_token)
        ).json()["data"]
        owner = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
        officer_token = self._make_officer(client, db_session)
        client.post("/api/v1/rentals/owners/verify", json={"user_id": owner.id}, headers=_headers(officer_token))
        published = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={"action": "publish"},
            headers=_headers(officer_token),
        )
        assert published.status_code == 200, published.text
        return published.json()["data"]["public_id"]

    def test_photos_public_once_listing_published(self, client, db_session, property_id, owner_token):
        client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        self._publish(client, db_session, property_id, owner_token)

        anon_list = client.get(f"/api/v1/properties/{property_id}/photos")
        assert anon_list.status_code == 200
        assert len(anon_list.json()["data"]) == 1

        photo_id = anon_list.json()["data"][0]["id"]
        anon_file = client.get(f"/api/v1/properties/{property_id}/photos/{photo_id}/file")
        assert anon_file.status_code == 200

    def test_public_listing_detail_exposes_photo_urls(self, client, db_session, property_id, owner_token):
        client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        public_id = self._publish(client, db_session, property_id, owner_token)

        detail = client.get(f"/api/v1/rentals/listings/{public_id}")
        assert detail.status_code == 200
        photo_urls = detail.json()["data"]["property"]["photo_urls"]
        assert len(photo_urls) == 1
        assert photo_urls[0].startswith(f"/api/v1/properties/{property_id}/photos/")
        assert photo_urls[0].endswith("/file")
        # And the opaque URL actually resolves, anonymously.
        assert client.get(photo_urls[0]).status_code == 200


class TestDelete:
    def test_owner_can_delete_own_photo(self, client, property_id, owner_token):
        upload = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        photo_id = upload.json()["data"]["id"]

        delete = client.delete(f"/api/v1/properties/{property_id}/photos/{photo_id}", headers=_headers(owner_token))
        assert delete.status_code == 200

        listed = client.get(f"/api/v1/properties/{property_id}/photos", headers=_headers(owner_token))
        assert listed.json()["data"] == []

    def test_other_owner_cannot_delete(self, client, property_id, owner_token, other_owner_token):
        upload = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        photo_id = upload.json()["data"]["id"]

        delete = client.delete(
            f"/api/v1/properties/{property_id}/photos/{photo_id}", headers=_headers(other_owner_token)
        )
        assert delete.status_code == 404

    def test_deleted_photo_file_removed_from_disk(self, client, property_id, owner_token):
        upload = client.post(
            f"/api/v1/properties/{property_id}/photos",
            files={"file": ("photo.png", _valid_image_bytes(), "image/png")},
            headers=_headers(owner_token),
        )
        photo_id = upload.json()["data"]["id"]

        client.delete(f"/api/v1/properties/{property_id}/photos/{photo_id}", headers=_headers(owner_token))

        missing = client.get(
            f"/api/v1/properties/{property_id}/photos/{photo_id}/file", headers=_headers(owner_token)
        )
        assert missing.status_code == 404