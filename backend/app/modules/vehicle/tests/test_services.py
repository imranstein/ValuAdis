"""
Vehicle Services Tests

Test cases for vehicle valuation services.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from app.modules.vehicle.services import VehicleValuationService
from app.modules.vehicle.models import Vehicle, VehicleValuation
from app.modules.vehicle.schemas import VehicleCreate, VehicleUpdate, VehicleValuationCreate


class TestVehicleService:
    """Test vehicle service operations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.service = VehicleValuationService(self.mock_db)
        self.mock_vehicle_repo = Mock()
        self.mock_valuation_repo = Mock()
        
        self.service.vehicle_repo = self.mock_vehicle_repo
        self.service.valuation_repo = self.mock_valuation_repo
    
    def test_create_vehicle_success(self):
        """Test successful vehicle creation"""
        # Setup
        vehicle_data = VehicleCreate(
            make="Toyota",
            model="Corolla",
            year=2020,
            vin="JH4KA8260MC000000",
            plate_number="AA-123-BC",
            owner_id=1
        )
        
        mock_vehicle = Vehicle(
            id=uuid4(),
            make="Toyota",
            model="Corolla",
            year=2020,
            vin="JH4KA8260MC000000",
            plate_number="AA-123-BC",
            owner_id=1
        )
        
        self.mock_vehicle_repo.get_by_vin.return_value = None
        self.mock_vehicle_repo.get_by_plate.return_value = None
        self.mock_vehicle_repo.create.return_value = mock_vehicle
        
        # Execute
        result = self.service.create_vehicle(vehicle_data, 1)
        
        # Assert
        assert result == mock_vehicle
        self.mock_vehicle_repo.get_by_vin.assert_called_once_with("JH4KA8260MC000000")
        self.mock_vehicle_repo.get_by_plate.assert_called_once_with("AA-123-BC")
        self.mock_vehicle_repo.create.assert_called_once()
    
    def test_create_vehicle_duplicate_vin(self):
        """Test vehicle creation with duplicate VIN"""
        # Setup
        vehicle_data = VehicleCreate(
            make="Toyota",
            model="Corolla",
            year=2020,
            vin="JH4KA8260MC000000",
            plate_number="AA-123-BC",
            owner_id=1
        )
        
        existing_vehicle = Mock()
        self.mock_vehicle_repo.get_by_vin.return_value = existing_vehicle
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Vehicle with VIN .* already exists"):
            self.service.create_vehicle(vehicle_data, 1)
    
    def test_create_vehicle_duplicate_plate(self):
        """Test vehicle creation with duplicate plate number"""
        # Setup
        vehicle_data = VehicleCreate(
            make="Toyota",
            model="Corolla",
            year=2020,
            vin="JH4KA8260MC000000",
            plate_number="AA-123-BC",
            owner_id=1
        )
        
        existing_vehicle = Mock()
        self.mock_vehicle_repo.get_by_vin.return_value = None
        self.mock_vehicle_repo.get_by_plate.return_value = existing_vehicle
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Vehicle with plate .* already exists"):
            self.service.create_vehicle(vehicle_data, 1)
    
    def test_get_vehicle_success(self):
        """Test successful vehicle retrieval"""
        # Setup
        vehicle_id = uuid4()
        mock_vehicle = Vehicle(
            id=vehicle_id,
            make="Toyota",
            model="Corolla",
            year=2020
        )
        
        self.mock_vehicle_repo.get_by_id.return_value = mock_vehicle
        
        # Execute
        result = self.service.get_vehicle(vehicle_id)
        
        # Assert
        assert result == mock_vehicle
        self.mock_vehicle_repo.get_by_id.assert_called_once_with(vehicle_id)
    
    def test_get_vehicle_not_found(self):
        """Test vehicle retrieval when not found"""
        # Setup
        vehicle_id = uuid4()
        self.mock_vehicle_repo.get_by_id.return_value = None
        
        # Execute
        result = self.service.get_vehicle(vehicle_id)
        
        # Assert
        assert result is None
        self.mock_vehicle_repo.get_by_id.assert_called_once_with(vehicle_id)
    
    def test_update_vehicle_success(self):
        """Test successful vehicle update"""
        # Setup
        vehicle_id = uuid4()
        update_data = VehicleUpdate(
            make="Honda",
            model="Civic",
            mileage=50000
        )
        
        mock_vehicle = Vehicle(
            id=vehicle_id,
            make="Toyota",
            model="Corolla",
            year=2020
        )
        
        updated_vehicle = Vehicle(
            id=vehicle_id,
            make="Honda",
            model="Civic",
            year=2020,
            mileage=50000
        )
        
        self.mock_vehicle_repo.get_by_id.return_value = mock_vehicle
        self.mock_vehicle_repo.get_by_vin.return_value = None
        self.mock_vehicle_repo.get_by_plate.return_value = None
        self.mock_vehicle_repo.update.return_value = updated_vehicle
        
        # Execute
        result = self.service.update_vehicle(vehicle_id, update_data)
        
        # Assert
        assert result == updated_vehicle
        self.mock_vehicle_repo.update.assert_called_once()
    
    def test_delete_vehicle_success(self):
        """Test successful vehicle deletion"""
        # Setup
        vehicle_id = uuid4()
        self.mock_vehicle_repo.delete.return_value = True
        
        # Execute
        result = self.service.delete_vehicle(vehicle_id)
        
        # Assert
        assert result is True
        self.mock_vehicle_repo.delete.assert_called_once_with(vehicle_id)


class TestVehicleValuationService:
    """Test vehicle valuation service operations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.service = VehicleValuationService(self.mock_db)
        self.mock_vehicle_repo = Mock()
        self.mock_valuation_repo = Mock()
        
        self.service.vehicle_repo = self.mock_vehicle_repo
        self.service.valuation_repo = self.mock_valuation_repo
    
    def test_create_valuation_success(self):
        """Test successful valuation creation"""
        # Setup
        vehicle_id = uuid4()
        valuation_data = VehicleValuationCreate(
            vehicle_id=vehicle_id,
            market_value=500000,
            valuation_method="Market Comparison"
        )
        
        mock_vehicle = Vehicle(
            id=vehicle_id,
            make="Toyota",
            model="Corolla",
            year=2020
        )
        
        mock_valuation = VehicleValuation(
            id=uuid4(),
            vehicle_id=vehicle_id,
            market_value=500000,
            taxable_value=125000,  # 25% of market value
            valuation_method="Market Comparison"
        )
        
        self.mock_vehicle_repo.get_by_id.return_value = mock_vehicle
        self.mock_valuation_repo.create.return_value = mock_valuation
        
        # Execute
        result = self.service.create_valuation(valuation_data, 1)
        
        # Assert
        assert result == mock_valuation
        assert result.taxable_value == 125000
        self.mock_vehicle_repo.get_by_id.assert_called_once_with(vehicle_id)
        self.mock_valuation_repo.create.assert_called_once()
    
    def test_create_valuation_vehicle_not_found(self):
        """Test valuation creation when vehicle not found"""
        # Setup
        vehicle_id = uuid4()
        valuation_data = VehicleValuationCreate(
            vehicle_id=vehicle_id,
            market_value=500000,
            valuation_method="Market Comparison"
        )
        
        self.mock_vehicle_repo.get_by_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Vehicle .* not found"):
            self.service.create_valuation(valuation_data, 1)
    
    def test_analyze_and_value_vehicle_success(self):
        """Test AI-powered vehicle analysis and valuation"""
        # Setup
        vehicle_id = uuid4()
        mock_vehicle = Vehicle(
            id=vehicle_id,
            make="Toyota",
            model="Corolla",
            year=2020,
            mileage=50000
        )
        
        similar_vehicles = []
        market_data = []
        
        mock_valuation = VehicleValuation(
            id=uuid4(),
            vehicle_id=vehicle_id,
            market_value=450000,
            taxable_value=112500
        )
        
        self.mock_vehicle_repo.get_by_id.return_value = mock_vehicle
        self.mock_vehicle_repo.get_similar_vehicles.return_value = similar_vehicles
        self.mock_valuation_repo.get_market_data.return_value = market_data
        
        with patch.object(self.service, 'create_valuation', return_value=mock_valuation):
            # Execute
            result = self.service.analyze_and_value_vehicle(vehicle_id, 1, True)
            
            # Assert
            assert result == mock_valuation
            self.mock_vehicle_repo.get_by_id.assert_called_once_with(vehicle_id)
            self.mock_vehicle_repo.get_similar_vehicles.assert_called_once()
            self.mock_valuation_repo.get_market_data.assert_called_once()
    
    def test_get_valuation_statistics(self):
        """Test valuation statistics calculation"""
        # Setup
        from datetime import datetime
        
        valuations = [
            VehicleValuation(
                id=uuid4(),
                market_value=500000,
                status="approved",
                valuation_date=datetime.now()
            ),
            VehicleValuation(
                id=uuid4(),
                market_value=300000,
                status="draft",
                valuation_date=datetime.now()
            )
        ]
        
        mock_vehicle_1 = Vehicle(make="Toyota", model="Corolla", region="Addis Ababa")
        mock_vehicle_2 = Vehicle(make="Honda", model="Civic", region="Oromia")
        
        valuations[0].vehicle = mock_vehicle_1
        valuations[1].vehicle = mock_vehicle_2
        
        self.mock_valuation_repo.search_valuations.return_value = valuations
        
        # Execute
        result = self.service.get_valuation_statistics()
        
        # Assert
        assert result["total_valuations"] == 2
        assert result["total_market_value"] == 800000
        assert result["average_value"] == 400000
        assert "Toyota" in result["by_make"]
        assert "Honda" in result["by_make"]
        assert "Addis Ababa" in result["by_region"]
        assert "approved" in result["by_status"]
    
    def test_approve_valuation_success(self):
        """Test valuation approval"""
        # Setup
        valuation_id = uuid4()
        approved_by = 2
        
        mock_valuation = VehicleValuation(
            id=valuation_id,
            status="submitted"
        )
        
        approved_valuation = VehicleValuation(
            id=valuation_id,
            status="approved",
            approved_by=approved_by,
            certificate_number="VAL-20260303120000-ABC123"
        )
        
        self.mock_valuation_repo.get_by_id.return_value = mock_valuation
        self.mock_valuation_repo.approve_valuation.return_value = approved_valuation
        
        # Execute
        result = self.service.approve_valuation(valuation_id, approved_by)
        
        # Assert
        assert result == approved_valuation
        assert result.status == "approved"
        assert result.approved_by == approved_by
        assert result.certificate_number is not None


class TestVehicleAIAnalysis:
    """Test AI analysis components"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.service = VehicleValuationService(self.mock_db)
    
    def test_basic_valuation_calculation(self):
        """Test basic valuation calculation without AI"""
        # Setup
        mock_vehicle = Vehicle(
            make="Toyota",
            model="Corolla",
            year=2020,
            mileage=50000,
            region="Addis Ababa",
            custom_duty_paid=True
        )
        
        similar_vehicles = []
        
        # Execute
        result = self.service._basic_valuation_calculation(mock_vehicle, similar_vehicles)
        
        # Assert
        assert "market_value" in result
        assert "method" in result
        assert "depreciation_rate" in result
        assert "condition_factor" in result
        assert "confidence_score" in result
        assert result["market_value"] > 0
        assert result["method"] == "Market Comparison"
    
    def test_market_trends(self):
        """Test market trends analysis"""
        # Execute
        result = self.service.get_market_trends()
        
        # Assert
        assert "popular_makes" in result
        assert "average_prices" in result
        assert "market_growth" in result
        assert "regional_variations" in result
        assert isinstance(result["popular_makes"], list)
        assert isinstance(result["average_prices"], dict)


if __name__ == "__main__":
    pytest.main([__file__])
