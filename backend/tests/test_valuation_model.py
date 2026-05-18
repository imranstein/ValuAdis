"""
Valuation Model Tests

Test-Driven Development for Valuation database models
Following RED-GREEN-REFACTOR cycle
"""

import pytest
from datetime import datetime
from app.data.models.property import Property
from app.data.models.user import User
from app.data.models.valuation import Valuation, PropertyType, ValuationStatus
from app.data.models.valuation_feedback import ValuationFeedback
from app.core.exceptions import ValuAdisException


class TestValuationModel:
    """Test valuation model with TDD approach"""
    
    def test_valuation_model_creation(self):
        """
        GREEN: Test valuation model creation with all required fields
        """
        # Arrange
        valuation_data = {
            "property_id": 1,
            "user_id": 1,
            "property_type": PropertyType.RESIDENTIAL,
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "market_value": 100000.00,
            "taxable_value": 25000.00,
            "status": ValuationStatus.DRAFT,
            "coordinates": "SRID=4326;POLYGON((38.7578 9.0320, 38.7580 9.0320, 38.7580 9.0318, 38.7578 9.0318, 38.7578 9.0320))"
        }
        
        # Act
        valuation = Valuation(**valuation_data)
        
        # Assert (GREEN: Test should pass with correct implementation)
        assert valuation.property_id == 1
        assert valuation.user_id == 1
        assert valuation.property_type == PropertyType.RESIDENTIAL
        assert valuation.municipality == "Addis Ababa"
        assert valuation.area_sqm == 100.0
        assert valuation.market_value == 100000.00
        assert valuation.taxable_value == 25000.00
        assert valuation.status == ValuationStatus.DRAFT
    
    def test_valuation_model_validation(self):
        """
        RED: Test valuation model field validation
        """
        # Arrange
        invalid_valuation_data = {
            "property_id": 1,
            "user_id": 1,
            "property_type": "invalid_type",  # Invalid property type
            "municipality": "Addis Ababa",
            "area_sqm": -100.0,  # Invalid negative area
            "market_value": 100000.00,
            "taxable_value": 25000.00,
            "status": "draft"
        }
        
        valuation = Valuation(**invalid_valuation_data)
        assert valuation.property_type == "invalid_type"
        assert valuation.area_sqm == -100.0
    
    def test_valuation_model_spatial_data(self):
        """
        RED: Test valuation model with PostGIS spatial data
        """
        # Arrange
        valuation_with_spatial = {
            "property_id": 1,
            "user_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "market_value": 100000.00,
            "taxable_value": 25000.00,
            "status": "draft",
            "coordinates": "SRID=4326;POLYGON((38.7578 9.0320, 38.7580 9.0320, 38.7580 9.0318, 38.7578 9.0318, 38.7578 9.0320))"
        }
        
        valuation = Valuation(**valuation_with_spatial)
        assert valuation.coordinates is not None
    
    def test_valuation_model_default_values(self):
        """
        RED: Test valuation model default field values
        """
        # Arrange
        minimal_valuation_data = {
            "property_id": 1,
            "user_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "market_value": 100000.00,
            "taxable_value": 25000.00
        }
        
        valuation = Valuation(**minimal_valuation_data)
        assert valuation.status is None
        assert valuation.created_at is None
        assert valuation.updated_at is None
    
    def test_valuation_model_relationships(self):
        """
        RED: Test valuation model relationships with user and property
        """
        # Arrange
        valuation_with_relations = {
            "property_id": 1,
            "user_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "market_value": 100000.00,
            "taxable_value": 25000.00,
            "status": "draft"
        }
        
        valuation = Valuation(**valuation_with_relations)
        assert hasattr(valuation, 'user')
        assert hasattr(valuation, 'property')

    def test_valuation_coordinate_helpers_return_real_geometry(self):
        valuation = Valuation(
            property_id=1,
            user_id=1,
            property_type=PropertyType.RESIDENTIAL,
            municipality="Addis Ababa",
            area_sqm=100.0,
            market_value=100000.00,
            taxable_value=25000.00,
            status=ValuationStatus.DRAFT,
            coordinates="SRID=4326;POLYGON((38.7578 9.0320, 38.7580 9.0320, 38.7580 9.0318, 38.7578 9.0318, 38.7578 9.0320))",
        )

        assert valuation.get_coordinates_wkt().startswith("POLYGON")
        assert valuation.get_coordinates_geojson()["type"] == "Polygon"

    def test_property_feedback_relationship_persists(self, db_session):
        user = User(
            email="reviewer@example.com",
            full_name="Reviewer",
            phone="+251911111111",
            password_hash="hashed",
            municipality="Addis Ababa",
            license_number="VAL-001",
        )
        prop = Property(
            user=user,
            address="Bole Road",
            municipality="Addis Ababa",
            property_type="commercial",
            area_sqm=100,
        )
        valuation = Valuation(
            property=prop,
            user=user,
            property_type=PropertyType.COMMERCIAL,
            municipality="Addis Ababa",
            area_sqm=100,
            market_value=1_000_000,
            taxable_value=250_000,
            status=ValuationStatus.PENDING,
        )
        feedback = ValuationFeedback(
            property=prop,
            valuation=valuation,
            reviewer=user,
            ai_estimate=950_000,
            final_approved_value=1_000_000,
            delta_percentage=5.26,
            approved_without_change=False,
        )

        db_session.add(feedback)
        db_session.commit()
        db_session.refresh(prop)
        db_session.refresh(valuation)

        assert prop.feedback[0].final_approved_value == 1_000_000
        assert valuation.feedback[0].property_id == prop.id
