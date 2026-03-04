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
        self._spatial_service = spatial_service
        self.db = db
        if db:
            from app.data.repositories.valuation_repository import ValuationRepository
            self.valuation_repo = ValuationRepository(db)

        # Ethiopian municipality base rates (Birr per square meter)
        # Tier 1: Capital / Major Commercial
        # Tier 2: Regional Capitals
        # Tier 3: Secondary Cities
        self._base_rates: Dict[str, Decimal] = {
            # Tier 1 – Capital / Major Commercial
            "Addis Ababa": Decimal("1000.00"),
            "Dire Dawa":   Decimal("800.00"),
            # Tier 2 – Regional Capitals
            "Mekelle":     Decimal("600.00"),
            "Bahir Dar":   Decimal("550.00"),
            "Adama":       Decimal("500.00"),
            "Hawassa":     Decimal("450.00"),
            "Gonder":      Decimal("400.00"),
            "Jimma":       Decimal("350.00"),
            # Tier 3 – Secondary Cities
            "Dessie":      Decimal("320.00"),
            "Jijiga":      Decimal("310.00"),
            "Shashamane":  Decimal("300.00"),
            "Arba Minch":  Decimal("290.00"),
            "Harar":       Decimal("280.00"),
            "Nekemte":     Decimal("270.00"),
            "Debre Markos":Decimal("260.00"),
            "Debre Birhan":Decimal("250.00"),
        }

        # Property type multipliers
        self._property_type_multipliers: Dict[str, Decimal] = {
            "residential":  Decimal("1.0"),
            "commercial":   Decimal("1.5"),
            "industrial":   Decimal("1.3"),
            "agricultural": Decimal("0.3"),
            "mixed_use":    Decimal("1.2"),
        }

        # Condition grade adjustments (Proclamation 1365/2025 Annex B)
        # Applied as a multiplier on the base calculation
        self._condition_factors: Dict[str, Decimal] = {
            "excellent": Decimal("1.20"),  # New / recently renovated
            "good":      Decimal("1.00"),  # Well-maintained
            "fair":      Decimal("0.80"),  # Some wear, minor repairs needed
            "poor":      Decimal("0.60"),  # Significant deterioration
        }

        # Neighborhood quality multipliers
        self._neighborhood_multipliers: Dict[str, Decimal] = {
            "prime":       Decimal("1.30"),  # CBD / high-demand zones
            "above_average": Decimal("1.10"),
            "average":     Decimal("1.00"),  # Default
            "below_average": Decimal("0.85"),
            "developing":  Decimal("0.70"),
        }

        # Annual depreciation rate for structures (straight-line)
        _ANNUAL_DEPRECIATION = Decimal("0.01")   # 1% per year
        _MAX_DEPRECIATION    = Decimal("0.50")    # Cap at 50%
        self._annual_depreciation = _ANNUAL_DEPRECIATION
        self._max_depreciation    = _MAX_DEPRECIATION

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_market_value(self, property_data: Dict[str, Any]) -> Decimal:
        """
        Calculate market value following Proclamation 1365/2025.

        Formula:
            land_value     = base_rate × area × type_multiplier
            structure_val  = land_value × structure_ratio × (1 – depreciation)
            neighborhood   = (land_value + structure_val) × neighborhood_multiplier
            market_value   = neighborhood × condition_factor

        Args:
            property_data: dict with keys:
                - municipality (str)
                - area_sqm (float | int | str)
                - property_type (str, optional) default "residential"
                - condition (str, optional)  default "good"
                - neighborhood_quality (str, optional)  default "average"
                - construction_year (int, optional)

        Returns:
            Market value in Ethiopian Birr (Decimal)
        """
        self._validate_property_data(property_data)

        municipality  = property_data["municipality"]
        area_sqm      = Decimal(str(property_data["area_sqm"]))
        property_type = property_data.get("property_type", "residential")
        condition     = property_data.get("condition", "good")
        neighborhood  = property_data.get("neighborhood_quality", "average")
        construction_year = property_data.get("construction_year")

        base_rate = self._base_rates.get(municipality)
        if not base_rate:
            # Fall back to the lowest tier rate for unlisted municipalities
            base_rate = Decimal("220.00")

        type_mult          = self._property_type_multipliers.get(property_type, Decimal("1.0"))
        condition_factor   = self._condition_factors.get(condition, Decimal("1.0"))
        neighborhood_mult  = self._neighborhood_multipliers.get(neighborhood, Decimal("1.0"))

        # Base land + structure value
        base_value = base_rate * area_sqm * type_mult

        # Apply age-based depreciation to structure component (40% of value)
        structure_ratio = Decimal("0.40")
        land_value      = base_value * (Decimal("1") - structure_ratio)
        structure_value = base_value * structure_ratio

        depreciation = self._calculate_depreciation(construction_year)
        structure_value_depreciated = structure_value * (Decimal("1") - depreciation)

        subtotal     = land_value + structure_value_depreciated
        after_nhd    = subtotal * neighborhood_mult
        market_value = after_nhd * condition_factor

        return market_value.quantize(Decimal("0.01"))

    def calculate_taxable_value(self, market_value: Decimal) -> Decimal:
        """
        Calculate taxable value per Proclamation 1365/2025 Art. 12.

        Taxable value = 25% of market value.
        """
        if market_value <= 0:
            raise PropertyValidationError("Market value must be greater than 0")
        return (market_value * Decimal("0.25")).quantize(Decimal("0.01"))

    def get_valuation_breakdown(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a full valuation breakdown for transparency / certificate generation.
        """
        self._validate_property_data(property_data)

        municipality       = property_data["municipality"]
        area_sqm           = Decimal(str(property_data["area_sqm"]))
        property_type      = property_data.get("property_type", "residential")
        condition          = property_data.get("condition", "good")
        neighborhood       = property_data.get("neighborhood_quality", "average")
        construction_year  = property_data.get("construction_year")

        is_fallback_rate   = municipality not in self._base_rates
        base_rate          = self._base_rates.get(municipality, Decimal("220.00"))
        type_mult          = self._property_type_multipliers.get(property_type, Decimal("1.0"))
        condition_factor   = self._condition_factors.get(condition, Decimal("1.0"))
        neighborhood_mult  = self._neighborhood_multipliers.get(neighborhood, Decimal("1.0"))
        depreciation       = self._calculate_depreciation(construction_year)

        base_value         = base_rate * area_sqm * type_mult
        structure_ratio    = Decimal("0.40")
        land_value         = (base_value * (Decimal("1") - structure_ratio)).quantize(Decimal("0.01"))
        structure_value    = (base_value * structure_ratio).quantize(Decimal("0.01"))
        structure_depreciated = (structure_value * (Decimal("1") - depreciation)).quantize(Decimal("0.01"))
        subtotal           = land_value + structure_depreciated
        after_nhd          = (subtotal * neighborhood_mult).quantize(Decimal("0.01"))
        market_value       = (after_nhd * condition_factor).quantize(Decimal("0.01"))
        taxable_value      = self.calculate_taxable_value(market_value)

        return {
            "municipality":              municipality,
            "area_sqm":                  float(area_sqm),
            "property_type":             property_type,
            "condition":                 condition,
            "neighborhood_quality":      neighborhood,
            "construction_year":         construction_year,
            "base_rate_per_sqm":         float(base_rate),
            "is_fallback_rate":          is_fallback_rate,
            "type_multiplier":           float(type_mult),
            "condition_factor":          float(condition_factor),
            "neighborhood_multiplier":   float(neighborhood_mult),
            "depreciation_rate":         float(depreciation),
            "land_value":                float(land_value),
            "structure_value_before_depreciation": float(structure_value),
            "structure_value_after_depreciation":  float(structure_depreciated),
            "subtotal":                  float(subtotal),
            "market_value":              float(market_value),
            "taxable_value":             float(taxable_value),
            "proclamation_reference":    "Proclamation 1365/2025 Art. 12",
        }

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def create_valuation(self, valuation_data: ValuationCreate, user_id: int) -> Dict[str, Any]:
        """Create a new valuation record."""
        property_data  = valuation_data.dict()
        market_value   = self.calculate_market_value(property_data)
        taxable_value  = self.calculate_taxable_value(market_value)

        coordinates_wkt = self._spatial_service.create_wkt_polygon(property_data["coordinates"])

        db_valuation = self.valuation_repo.create({
            "property_id":  valuation_data.property_id,
            "user_id":      user_id,
            "property_type": valuation_data.property_type,
            "municipality": valuation_data.municipality,
            "area_sqm":     valuation_data.area_sqm,
            "market_value": market_value,
            "taxable_value": taxable_value,
            "status":       "draft",
            "coordinates":  coordinates_wkt,
        })

        return db_valuation.to_dict() if hasattr(db_valuation, "to_dict") else {
            "id":            db_valuation.id,
            "property_id":  db_valuation.property_id,
            "market_value": db_valuation.market_value,
            "taxable_value": db_valuation.taxable_value,
            "status":       db_valuation.status,
        }

    def get_user_valuations(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        valuations_list = self.valuation_repo.get_user_valuations(user_id=user_id, skip=skip, limit=limit)
        total = self.db.query(self.valuation_repo.model).filter_by(user_id=user_id).count()
        return [v.to_dict() if hasattr(v, "to_dict") else v.__dict__ for v in valuations_list], total

    def get_valuation_by_id(self, valuation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            return valuation.to_dict() if hasattr(valuation, "to_dict") else valuation.__dict__
        return None

    def update_valuation(self, valuation_id: int, updates: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            updated = self.valuation_repo.update(valuation, updates)
            return updated.to_dict() if hasattr(updated, "to_dict") else updated.__dict__
        raise ValuAdisException("Valuation not found or unauthorized")

    def delete_valuation(self, valuation_id: int, user_id: int) -> bool:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            self.db.delete(valuation)
            self.db.commit()
            return True
        return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _calculate_depreciation(self, construction_year: Optional[int]) -> Decimal:
        """Straight-line depreciation from construction year, capped at 50%."""
        if not construction_year:
            return Decimal("0")
        from datetime import date
        age = max(0, date.today().year - construction_year)
        depreciation = min(
            self._annual_depreciation * Decimal(str(age)),
            self._max_depreciation,
        )
        return depreciation

    def _validate_property_data(self, property_data: Dict[str, Any]) -> None:
        """Validate property data meets Ethiopian standards."""
        for field in ("municipality", "area_sqm"):
            if field not in property_data:
                raise PropertyValidationError(f"Missing required field: {field}")

        municipality = property_data["municipality"]
        if not isinstance(municipality, str) or len(municipality.strip()) < 2:
            raise PropertyValidationError("Municipality must be a valid string")

        area_sqm = property_data["area_sqm"]
        try:
            area_decimal = Decimal(str(area_sqm))
            if area_decimal <= 0:
                raise PropertyValidationError("Area must be greater than 0")
            if area_decimal > 100000:
                raise PropertyValidationError("Area exceeds maximum allowed size (100 000 sqm)")
        except (ValueError, TypeError) as e:
            raise PropertyValidationError("Invalid area value") from e

        condition = property_data.get("condition", "good")
        if condition not in self._condition_factors:
            valid = ", ".join(self._condition_factors.keys())
            raise PropertyValidationError(f"Invalid condition '{condition}'. Must be one of: {valid}")

        neighborhood = property_data.get("neighborhood_quality", "average")
        if neighborhood not in self._neighborhood_multipliers:
            valid = ", ".join(self._neighborhood_multipliers.keys())
            raise PropertyValidationError(
                f"Invalid neighborhood_quality '{neighborhood}'. Must be one of: {valid}"
            )

        if "coordinates" in property_data:
            coordinates = property_data["coordinates"]
            if not self._spatial_service.validate_polygon(coordinates):
                raise PropertyValidationError(
                    "Coordinates must form a valid closed polygon (≥ 4 points, first == last)"
                )
            if not self._spatial_service.validate_ethiopian_coordinates(coordinates):
                raise PropertyValidationError("Coordinates must be within Ethiopia")
