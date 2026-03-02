"""
Valuation Model Tests

Test-Driven Development for Valuation database models
Following RED-GREEN-REFACTOR cycle
"""

import pytest
from datetime import datetime
from app.data.models.valuation import Valuation, PropertyType, ValuationStatus
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
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            valuation = Valuation(**invalid_valuation_data)
    
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
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            valuation = Valuation(**valuation_with_spatial)
            # Verify spatial data is properly stored
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
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            valuation = Valuation(**minimal_valuation_data)
            # Verify default values
            assert valuation.status == "draft"
            assert valuation.created_at is not None
            assert valuation.updated_at is not None
    
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
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            valuation = Valuation(**valuation_with_relations)
            # Verify relationships are accessible
            assert hasattr(valuation, 'user')
            assert hasattr(valuation, 'property')
