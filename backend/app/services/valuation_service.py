"""
Valuation Service

Business logic for property valuation calculations following Ethiopian standards
and Proclamation 1365/2025 compliance requirements.
"""

from decimal import Decimal
from typing import Dict, Any, Optional, Tuple, List
from app.services.spatial_service import SpatialService
from app.core.exceptions import ValuAdisException, PropertyValidationError
from app.schemas.valuation import ValuationCreate
from sqlalchemy.orm import Session


class ValuationService:
    """
    Property valuation service for Ethiopian properties
    
    Implements market value and taxable value calculations per
    Proclamation 1365/2025 requirements.
    """
    
    def __init__(self, spatial_service: SpatialService, db: Optional[Session] = None):
        """Initialize valuation service with spatial service dependency"""
        self._spatial_service = spatial_service
        self.db = db
        if db:
            from app.data.repositories.valuation_repository import ValuationRepository
            self.valuation_repo = ValuationRepository(db)
        
        # Ethiopian municipality base rates (Birr per square meter)
        # These rates are illustrative and should be updated based on
        # official Ethiopian property valuation guidelines
        self._base_rates = {
            "Addis Ababa": Decimal("1000.00"),  # Capital city premium
            "Dire Dawa": Decimal("800.00"),     # Major commercial city
            "Mekelle": Decimal("600.00"),       # Regional capital
            "Bahir Dar": Decimal("550.00"),      # Regional capital
            "Adama": Decimal("500.00"),          # Industrial city
            "Hawassa": Decimal("450.00"),       # Regional capital
            "Gonder": Decimal("400.00"),        # Historical city
            "Jimma": Decimal("350.00")          # Regional city
        }
        
        # Property type multipliers
        self._property_type_multipliers = {
            "residential": Decimal("1.0"),
            "commercial": Decimal("1.5"),
            "agricultural": Decimal("0.3")
        }
    
    def calculate_market_value(self, property_data: Dict[str, Any]) -> Decimal:
        """
        Calculate market value for a property using Ethiopian valuation standards
        
        Formula: Base Rate × Area × Property Type Multiplier
        
        Args:
            property_data: Dictionary containing property information
                - property_type: Type of property (residential, commercial, agricultural)
                - municipality: Ethiopian municipality
                - area_sqm: Property area in square meters
                
        Returns:
            Market value in Ethiopian Birr
            
        Raises:
            PropertyValidationError: If property data is invalid
            ValuAdisException: If municipality is not supported
        """
        # Validate input data
        self._validate_property_data(property_data)
        
        # Extract property information
        municipality = property_data["municipality"]
        area_sqm = Decimal(str(property_data["area_sqm"]))
        property_type = property_data.get("property_type", "residential")
        
        # Get base rate for municipality
        base_rate = self._base_rates.get(municipality)
        if not base_rate:
            raise ValuAdisException(f"Unsupported municipality: {municipality}")
        
        # Get property type multiplier
        multiplier = self._property_type_multipliers.get(property_type, Decimal("1.0"))
        
        # Calculate market value
        market_value = base_rate * area_sqm * multiplier
        
        return market_value
    
    def calculate_taxable_value(self, market_value: Decimal) -> Decimal:
        """
        Calculate taxable value per Proclamation 1365/2025
        
        Per Ethiopian law, taxable value is 25% of market value
        
        Args:
            market_value: Market value in Ethiopian Birr
            
        Returns:
            Taxable value in Ethiopian Birr (25% of market value)
            
        Raises:
            PropertyValidationError: If market value is invalid
        """
        if market_value <= 0:
            raise PropertyValidationError("Market value must be greater than 0")
        
        # Per Proclamation 1365/2025: Taxable value = 25% of market value
        taxable_rate = Decimal("0.25")
        taxable_value = market_value * taxable_rate
        
        return taxable_value
    
    def _validate_property_data(self, property_data: Dict[str, Any]) -> None:
        """
        Validate property data meets Ethiopian standards
        
        Args:
            property_data: Property data to validate
            
        Raises:
            PropertyValidationError: If property data is invalid
        """
        required_fields = ["municipality", "area_sqm"]
        for field in required_fields:
            if field not in property_data:
                raise PropertyValidationError(f"Missing required field: {field}")
        
        # Validate municipality
        municipality = property_data["municipality"]
        if not isinstance(municipality, str) or len(municipality.strip()) < 2:
            raise PropertyValidationError("Municipality must be a valid string")
        
        # Validate area
        area_sqm = property_data["area_sqm"]
        try:
            area_decimal = Decimal(str(area_sqm))
            if area_decimal <= 0:
                raise PropertyValidationError("Area must be greater than 0")
            if area_decimal > 100000:  # 100,000 sqm = 10 hectares
                raise PropertyValidationError("Area exceeds maximum allowed size")
        except (ValueError, TypeError):
            raise PropertyValidationError("Invalid area value")
        
        # Validate coordinates if provided
        if "coordinates" in property_data:
            coordinates = property_data["coordinates"]
            if not isinstance(coordinates, list) or len(coordinates) < 4:
                raise PropertyValidationError("Coordinates must form a valid polygon")
            
            # Check if polygon is closed
            if coordinates[0] != coordinates[-1]:
                raise PropertyValidationError("Coordinates must form a closed polygon")
            
            # Validate coordinate ranges
            for coord in coordinates:
                if not isinstance(coord, (list, tuple)) or len(coord) != 2:
                    raise PropertyValidationError("Invalid coordinate format")
                lon, lat = coord
                if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                    raise PropertyValidationError("Invalid coordinate range")
                
                # Check if coordinates are within Ethiopia bounds (approximate)
                if not (33 <= lon <= 48) or not (3 <= lat <= 15):
                    raise PropertyValidationError("Coordinates must be within Ethiopia")
    
    def create_valuation(self, valuation_data: ValuationCreate, user_id: int) -> Dict[str, Any]:
        """Create a new valuation record"""
        property_data = valuation_data.dict()
        market_value = self.calculate_market_value(property_data)
        taxable_value = self.calculate_taxable_value(market_value)
        
        # Create boundary geometry for PostGIS
        coordinates_wkt = self._spatial_service.create_wkt_polygon(property_data['coordinates'])
        
        db_valuation = self.valuation_repo.create({
            "property_id": valuation_data.property_id,
            "user_id": user_id,
            "property_type": valuation_data.property_type,
            "municipality": valuation_data.municipality,
            "area_sqm": valuation_data.area_sqm,
            "market_value": market_value,
            "taxable_value": taxable_value,
            "status": "draft",
            "coordinates": coordinates_wkt
        })
        
        return db_valuation.to_dict() if hasattr(db_valuation, 'to_dict') else {
            "id": db_valuation.id,
            "property_id": db_valuation.property_id,
            "market_value": db_valuation.market_value,
            "taxable_value": db_valuation.taxable_value,
            "status": db_valuation.status
        }

    def get_user_valuations(self, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Dict[str, Any]], int]:
        """Get all valuations for a specific user."""
        valuations_list = self.valuation_repo.get_user_valuations(user_id=user_id, skip=skip, limit=limit)
        total = self.db.query(self.valuation_repo.model).filter_by(user_id=user_id).count()
        return [v.to_dict() if hasattr(v, 'to_dict') else v.__dict__ for v in valuations_list], total

    def get_valuation_by_id(self, valuation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            return valuation.to_dict() if hasattr(valuation, 'to_dict') else valuation.__dict__
        return None

    def update_valuation(self, valuation_id: int, updates: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            updated = self.valuation_repo.update(valuation, updates)
            return updated.to_dict() if hasattr(updated, 'to_dict') else updated.__dict__
        raise ValuAdisException("Valuation not found or unauthorized")

    def delete_valuation(self, valuation_id: int, user_id: int) -> bool:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            self.db.delete(valuation)
            self.db.commit()
            return True
        return False
