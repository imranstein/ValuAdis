"""
Valuation Service Tests

Test-Driven Development for ValuAdis valuation calculations
Following RED-GREEN-REFACTOR cycle
"""

import pytest
from decimal import Decimal
from app.services.valuation_service import ValuationService
from app.services.spatial_service import SpatialService
from app.core.exceptions import ValuAdisException, PropertyValidationError
from app.schemas.valuation import ValuationCreate


class TestValuationService:
    """Test valuation service with TDD approach"""
    
    def test_calculate_market_value_residential_addis_ababa(self):
        """
        GREEN: Test market value calculation for residential property in Addis Ababa
        
        Expected: Base rate per sqm * area = 1000 * 100 = 100,000 Birr
        """
        # Arrange
        property_data = {
            "property_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]  # Properly closed polygon
        }
        
        spatial_service = SpatialService()
        valuation_service = ValuationService(spatial_service)
        
        # Act
        result = valuation_service.calculate_market_value(property_data)
        
        # Assert (GREEN: Test should pass with correct implementation)
        assert result == Decimal("100000.00")
    
    def test_calculate_taxable_value_25_percent_proclamation(self):
        """
        GREEN: Test taxable value calculation per Proclamation 1365/2025
        
        Expected: 25% of market value = 250,000 Birr
        """
        # Arrange
        market_value = Decimal("1000000.00")  # 1 million Birr
        
        spatial_service = SpatialService()
        valuation_service = ValuationService(spatial_service)
        
        # Act
        taxable_value = valuation_service.calculate_taxable_value(market_value)
        
        # Assert (GREEN: Test should pass with correct implementation)
        assert taxable_value == Decimal("250000.00")
    
    def test_validate_property_data_ethiopian_coordinates(self):
        """
        RED: Test property validation for Ethiopian coordinates
        
        Expected: Valid Ethiopian coordinates pass validation
        """
        # Arrange
        property_data = {
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318]]
        }
        
        spatial_service = SpatialService()
        valuation_service = ValuationService(spatial_service)
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            valuation_service._validate_property_data(property_data)
    
    def test_calculate_market_value_invalid_municipality(self):
        """
        RED: Test market value calculation with unsupported municipality
        
        Expected: Should raise ValidationError
        """
        # Arrange
        property_data = {
            "property_id": 1,
            "property_type": "residential",
            "municipality": "Unsupported City",
            "area_sqm": 100.0,
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318]]
        }
        
        spatial_service = SpatialService()
        valuation_service = ValuationService(spatial_service)
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            result = valuation_service.calculate_market_value(property_data)
    
    def test_create_valuation_record(self):
        """
        RED: Test creating a valuation record
        
        Expected: Should create valuation with calculated values
        """
        # Arrange
        valuation_data = ValuationCreate(
            property_id=1,
            property_type="residential",
            municipality="Addis Ababa",
            area_sqm=100.0,
            coordinates=[[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318]]
        )
        
        spatial_service = SpatialService()
        valuation_service = ValuationService(spatial_service)
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            result = valuation_service.create_valuation(valuation_data, user_id=1)
