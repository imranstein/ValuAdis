"""
Properties Routes

Single owner of the /api/v1/properties contract after the v2 consolidation.
Moved verbatim from app/api/v1/endpoints/properties.py; api.py mounts this
router with prefix="/properties".
"""

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Tuple
import csv
import io
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.exceptions import SpatialOperationException, ValidationException
from app.services.spatial_service import SpatialService
from .schemas import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListResponse,
    SpatialRequest,
    OverlapRequest,
)
from .services import PropertyService

router = APIRouter()


def _to_tuples(coords: List[List[float]]) -> List[Tuple[float, float]]:
    result: List[Tuple[float, float]] = []
    for i, c in enumerate(coords):
        if not isinstance(c, (list, tuple)) or len(c) < 2:
            raise ValueError(
                f"Coordinate at index {i} must have at least 2 elements, got: {c!r}"
            )
        if not all(isinstance(v, (int, float)) for v in c[:2]):
            raise ValueError(
                f"Coordinate at index {i} must contain numbers, got: {c!r}"
            )
        result.append((float(c[0]), float(c[1])))
    return result


def _csv_value(value: str):
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _float_csv_value(value: str):
    normalized = _csv_value(value)
    return float(normalized) if normalized is not None else None


def _build_property_import_row(row: dict) -> dict:
    data = {key: _csv_value(value) for key, value in row.items()}
    for field in ["latitude", "longitude", "area_sqm", "building_area_sqm", "land_value", "building_value", "market_value", "taxable_value"]:
        if field in data:
            data[field] = _float_csv_value(data[field])
    if data.get("market_value") is not None:
        expected_taxable = round(data["market_value"] * 0.25, 2)
        supplied_taxable = data.get("taxable_value")
        if supplied_taxable is not None and round(supplied_taxable, 2) != expected_taxable:
            raise ValueError("Taxable value must be exactly 25% of market value")
        data["taxable_value"] = expected_taxable
    return data


@router.post("/spatial/summary", tags=["Properties"])
async def spatial_summary(
    body: SpatialRequest,
    _: int = Depends(get_current_user_id),
):
    """
    Return a full spatial summary (area, perimeter, centroid, bounding box)
    for a set of GPS boundary coordinates.
    """
    try:
        coords = _to_tuples(body.coordinates)
        svc = SpatialService()
        return {"success": True, "data": svc.get_spatial_summary(coords)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SpatialOperationException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/spatial/overlap", tags=["Properties"])
async def check_overlap(
    body: OverlapRequest,
    _: int = Depends(get_current_user_id),
):
    """
    Check whether two property boundaries overlap and return the overlap
    area (m²) and percentage.
    """
    try:
        svc = SpatialService()
        a = _to_tuples(body.coordinates_a)
        b = _to_tuples(body.coordinates_b)
        overlaps = svc.polygons_overlap(a, b)
        overlap_area = svc.calculate_overlap_area(a, b) if overlaps else 0.0
        overlap_pct  = svc.get_overlap_percentage(a, b) if overlaps else 0.0
        return {
            "success":       True,
            "overlaps":      overlaps,
            "overlap_area_sqm": round(overlap_area, 2),
            "overlap_percentage": round(overlap_pct, 4),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SpatialOperationException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Create new property with GPS boundary"""
    property_service = PropertyService(db)
    
    try:
        property = await property_service.create_property(
            property_data.model_dump(),
            user_id=current_user_id
        )
        return PropertyResponse(success=True, data=property.to_dict())
    except (ValueError, ValidationException, SpatialOperationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/bulk-import", tags=["Properties"])
async def bulk_import_properties(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Import properties from a CSV file."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    property_service = PropertyService(db)
    rows = []
    errors = []

    for row_number, row in enumerate(reader, start=2):
        try:
            property_data = _build_property_import_row(row)
            rows.append(PropertyCreate(**property_data).model_dump())
        except Exception as exc:
            errors.append({"row": row_number, "message": str(exc)})

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    imported = []
    for row in rows:
        try:
            property = await property_service.create_property(row, user_id=current_user_id)
            imported.append(property.to_dict())
        except Exception as exc:
            raise HTTPException(status_code=422, detail=[{"row": len(imported) + 2, "message": str(exc)}])

    return {
        "success": True,
        "imported_count": len(imported),
        "data": imported,
    }


@router.get("/export", tags=["Properties"])
async def export_properties(
    format: str = "csv",
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Export properties as CSV"""
    if format.lower() != "csv":
        raise HTTPException(status_code=400, detail="Only CSV format is supported")
    property_service = PropertyService(db)
    properties, _ = await property_service.get_user_properties(
        user_id=current_user_id, skip=0, limit=10000
    )
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ["id", "address", "municipality", "property_type", "area_sqm", "market_value", "status", "created_at"]
    writer.writerow(headers)
    for p in properties:
        d = p.to_dict()
        writer.writerow([
            d.get("id"),
            d.get("address", ""),
            d.get("municipality", ""),
            d.get("property_type", ""),
            d.get("area_sqm"),
            d.get("market_value"),
            d.get("status", ""),
            d.get("created_at", ""),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=properties_export.csv"},
    )


@router.get("", response_model=PropertyListResponse)
async def get_properties(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get user's properties with pagination"""
    property_service = PropertyService(db)
    
    properties, total = await property_service.get_user_properties(
        user_id=current_user_id,
        skip=skip,
        limit=limit
    )
    
    return PropertyListResponse(
        success=True,
        data=[p.to_dict() for p in properties],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get specific property by ID"""
    property_service = PropertyService(db)
    
    property = await property_service.get_property_by_id(
        property_id=property_id,
        user_id=current_user_id
    )
    
    if not property:
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
    
    return PropertyResponse(success=True, data=property.to_dict())


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Update property information"""
    property_service = PropertyService(db)
    
    try:
        property = await property_service.update_property(
            property_id=property_id,
            user_id=current_user_id,
            update_data=property_data.model_dump(exclude_unset=True)
        )
        
        if not property:
            raise HTTPException(
                status_code=404,
                detail="Property not found"
            )
        
        return PropertyResponse(success=True, data=property.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{property_id}")
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete property"""
    property_service = PropertyService(db)
    
    success = await property_service.delete_property(
        property_id=property_id,
        user_id=current_user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
    
    return {"success": True, "message": "Property deleted successfully"}
