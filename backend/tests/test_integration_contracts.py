from app.core.security import get_current_user_id
from app.data.models.property import Property
from app.data.models.user import User
from app.data.models.valuation import Valuation, PropertyType
import pytest
from sqlalchemy import text

from app.core.config import Settings, validate_production_settings


def test_dashboard_contract_returns_empty_metrics(client):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    response = client.get("/api/v1/analytics/dashboard?period=month")

    assert response.status_code == 200
    assert response.json()["valuations"]["total"] == 0


def test_vehicle_summary_contract_returns_empty_metrics(client):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    response = client.get("/api/v1/vehicles/statistics/summary")

    assert response.status_code == 200
    assert response.json()["total_vehicles"] == 0


def test_admin_flag_can_read_user_registry(client, db_session):
    admin = User(
        id=10,
        email="admin-flag@valuadis.com",
        full_name="Admin Flag",
        phone="+251911000010",
        password_hash="hashed",
        municipality="Addis Ababa",
        license_number="VAL-ADMIN-010",
        is_active=True,
        is_verified=True,
        is_admin=True,
        is_valuer=True,
    )
    db_session.add(admin)
    db_session.commit()
    client.app.dependency_overrides[get_current_user_id] = lambda: admin.id

    response = client.get("/api/v1/users")

    assert response.status_code == 200


def test_audit_logs_contract_returns_empty_ledger(client):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    response = client.get("/api/v1/audit/logs")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"] == []
    assert payload["total"] == 0


def test_audit_reports_require_authentication(client):
    response = client.get("/api/v1/audit/compliance")

    assert response.status_code == 401


def test_compliance_report_contract_returns_schema(client):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    response = client.get("/api/v1/audit/compliance")

    assert response.status_code == 200
    payload = response.json()
    rule = payload["compliance_report"]["proclamation_1365_2025_compliance"]
    assert payload["success"] is True
    assert "compliant_valuations" in rule
    assert "non_compliant_valuations" in rule


def test_compliance_report_handles_existing_valuations(client, db_session):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    user = User(
        id=20,
        email="compliance@valuadis.com",
        full_name="Compliance User",
        phone="+251911000020",
        password_hash="hashed",
        municipality="Addis Ababa",
        license_number="VAL-COMP-020",
        is_active=True,
        is_verified=True,
    )
    prop = Property(
        id=20,
        user_id=20,
        address="Bole, Addis Ababa",
        municipality="Addis Ababa",
        property_type="residential",
        area_sqm=100,
    )
    valuation = Valuation(
        property_id=20,
        user_id=20,
        property_type=PropertyType.RESIDENTIAL,
        municipality="Addis Ababa",
        area_sqm=100,
        market_value=1000.0,
        taxable_value=250.0,
    )
    db_session.add_all([user, prop, valuation])
    db_session.commit()

    response = client.get("/api/v1/audit/compliance")

    assert response.status_code == 200
    rule = response.json()["compliance_report"]["proclamation_1365_2025_compliance"]
    assert rule["total_valuations"] == 1
    assert rule["compliant_valuations"] == 1


def test_compliance_report_handles_string_created_at(client, db_session):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    db_session.execute(text(
        "INSERT INTO users (id, email, full_name, phone, password_hash, municipality, license_number, is_active) "
        "VALUES (21, 'compliance-string@valuadis.com', 'Compliance String', '+251911000021', 'hashed', 'Addis Ababa', 'VAL-COMP-021', 1)"
    ))
    db_session.execute(text(
        "INSERT INTO properties (id, user_id, address, municipality, property_type, area_sqm) "
        "VALUES (21, 21, 'Kazanchis, Addis Ababa', 'Addis Ababa', 'commercial', 100)"
    ))
    db_session.execute(text(
        "INSERT INTO valuations (property_id, user_id, property_type, municipality, area_sqm, market_value, taxable_value, status, created_at, updated_at) "
        "VALUES (21, 21, 'COMMERCIAL', 'Addis Ababa', 100, 1000.0, 300.0, 'DRAFT', '2026-05-17 10:00:00', '2026-05-17 10:00:00')"
    ))
    db_session.commit()

    response = client.get("/api/v1/audit/compliance")

    assert response.status_code == 200
    detail = response.json()["compliance_report"]["compliance_details"][0]
    assert detail["created_at"] == "2026-05-17 10:00:00"


def test_quick_valuation_uses_supported_municipality_rate(client):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    response = client.post(
        "/api/v1/valuations/quick",
        json={
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 250,
            "condition": "good",
            "neighborhood_quality": "prime",
            "construction_year": 2018,
        },
    )

    assert response.status_code == 200
    assert response.json()["base_rate"] == 1000.0


def test_valuation_preview_endpoints_require_authentication(client):
    quick_response = client.post(
        "/api/v1/valuations/quick",
        json={
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 250,
            "condition": "good",
        },
    )
    metrics_response = client.get("/api/v1/valuation-feedback/metrics")

    assert quick_response.status_code == 401
    assert metrics_response.status_code == 401


def test_valuation_detail_contract_returns_envelope(client):
    client.app.dependency_overrides[get_current_user_id] = lambda: 1

    create_response = client.post(
        "/api/v1/valuations/",
        json={
            "property_id": 42,
            "property_type": "commercial",
            "municipality": "Addis Ababa",
            "area_sqm": 250,
            "coordinates": [
                [38.7466, 9.0318],
                [38.747, 9.0318],
                [38.747, 9.0322],
                [38.7466, 9.0322],
                [38.7466, 9.0318],
            ],
            "condition": "good",
            "neighborhood_quality": "prime",
            "construction_year": 2018,
        },
    )
    valuation_id = create_response.json()["data"]["id"]

    response = client.get(f"/api/v1/valuations/{valuation_id}")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == valuation_id


def test_production_allowed_hosts_accept_comma_separated_values():
    settings = Settings(ALLOWED_HOSTS="https://valuadis.vulcanig.net,https://www.valuadis.vulcanig.net")

    assert settings.ALLOWED_HOSTS == [
        "https://valuadis.vulcanig.net",
        "https://www.valuadis.vulcanig.net",
    ]


def test_default_allowed_hosts_do_not_allow_all_origins():
    settings = Settings()

    assert "*" not in settings.ALLOWED_HOSTS


def test_production_settings_reject_placeholder_secret():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="CHANGE_THIS_SECRET_KEY_MIN_32_CHARS",
        DATABASE_URL="postgresql://valuadis:real-password@db.internal:5432/valuadis",
        REDIS_URL="redis://:real-password@redis.internal:6379/0",
        ALLOWED_HOSTS="https://valuadis.et",
    )

    with pytest.raises(ValueError, match="SECRET_KEY"):
        validate_production_settings(settings)


def test_production_settings_reject_placeholder_database_url():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="prod-secret-key-with-more-than-thirty-two-characters",
        DATABASE_URL="postgresql://valuadis:CHANGE_THIS_PASSWORD@db.internal:5432/valuadis",
        REDIS_URL="redis://:real-password@redis.internal:6379/0",
        ALLOWED_HOSTS="https://valuadis.et",
    )

    with pytest.raises(ValueError, match="DATABASE_URL"):
        validate_production_settings(settings)


def test_production_settings_accept_strict_deployed_config():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="prod-secret-key-with-more-than-thirty-two-characters",
        DATABASE_URL="postgresql://valuadis:real-password@db.internal:5432/valuadis",
        REDIS_URL="redis://:real-password@redis.internal:6379/0",
        ALLOWED_HOSTS="https://valuadis.et,https://www.valuadis.et",
    )

    validate_production_settings(settings)
