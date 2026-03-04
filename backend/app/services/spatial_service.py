"""
Spatial Service

PostGIS spatial operations and GPS coordinate processing for ValuAdis.
All calculations use the WGS-84 ellipsoid (EPSG:4326).
"""

from typing import Dict, List, Optional, Tuple

from pyproj import Geod
from shapely.geometry import MultiPolygon, Point, Polygon, mapping, shape
from shapely.ops import unary_union

from app.core.exceptions import SpatialOperationException


# WGS-84 geodetic calculator — re-used across all methods
_GEOD = Geod(ellps="WGS84")


class SpatialService:
    """PostGIS / Shapely spatial operations for Ethiopian property boundaries."""

    def __init__(self) -> None:
        self.geod = _GEOD

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_polygon(self, coordinates: List[Tuple[float, float]]) -> bool:
        """
        Return True when *coordinates* form a valid, non-empty polygon.

        Requires:
        - ≥ 4 points (3 vertices + closing point)
        - Closed ring (first == last)
        - All (lon, lat) values within valid ranges
        """
        if not coordinates or len(coordinates) < 4:
            return False
        if coordinates[0] != coordinates[-1]:
            return False
        for lon, lat in coordinates:
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                return False
        try:
            poly = Polygon(coordinates)
            return poly.is_valid and not poly.is_empty
        except Exception:
            return False

    def validate_ethiopian_coordinates(self, coordinates: List[Tuple[float, float]]) -> bool:
        """
        Return True when all *coordinates* fall within Ethiopia's bounding box.

        Approximate bounds:  Longitude 33°E – 48°E, Latitude 3°N – 15°N
        """
        for lon, lat in coordinates:
            if not (33 <= lon <= 48) or not (3 <= lat <= 15):
                return False
        return True

    # ------------------------------------------------------------------
    # Area & perimeter calculations
    # ------------------------------------------------------------------

    def calculate_area(self, coordinates: List[Tuple[float, float]]) -> float:
        """
        Calculate geodesic area in **square metres** (WGS-84).

        Args:
            coordinates: List of (longitude, latitude) tuples.

        Returns:
            Area in m².
        """
        try:
            poly = Polygon(coordinates)
            area, _ = self.geod.geometry_area_perimeter(poly)
            return abs(area)
        except Exception as exc:
            raise SpatialOperationException(f"Failed to calculate area: {exc}") from exc

    def calculate_area_hectares(self, coordinates: List[Tuple[float, float]]) -> float:
        """Return geodesic area in **hectares**."""
        return self.calculate_area(coordinates) / 10_000

    def calculate_area_acres(self, coordinates: List[Tuple[float, float]]) -> float:
        """Return geodesic area in **acres** (1 acre ≈ 4 046.856 m²)."""
        return self.calculate_area(coordinates) / 4_046.856

    def calculate_perimeter(self, coordinates: List[Tuple[float, float]]) -> float:
        """
        Calculate geodesic perimeter in **metres** (WGS-84).

        Args:
            coordinates: List of (longitude, latitude) tuples (closed or open ring).

        Returns:
            Perimeter in metres.
        """
        try:
            pts = list(coordinates)
            # Ensure the ring is closed for the perimeter walk
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            total = 0.0
            for i in range(len(pts) - 1):
                lon1, lat1 = pts[i]
                lon2, lat2 = pts[i + 1]
                _, _, dist = self.geod.inv(lon1, lat1, lon2, lat2)
                total += abs(dist)
            return total
        except Exception as exc:
            raise SpatialOperationException(f"Failed to calculate perimeter: {exc}") from exc

    # ------------------------------------------------------------------
    # Distance calculations
    # ------------------------------------------------------------------

    def calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float],
    ) -> float:
        """
        Calculate geodesic distance between two points in **metres**.

        Args:
            point1: (longitude, latitude).
            point2: (longitude, latitude).
        """
        try:
            _, _, distance = self.geod.inv(point1[0], point1[1], point2[0], point2[1])
            return abs(distance)
        except Exception as exc:
            raise SpatialOperationException(f"Failed to calculate distance: {exc}") from exc

    # ------------------------------------------------------------------
    # Centroid / simplification
    # ------------------------------------------------------------------

    def get_polygon_centroid(self, coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Return (longitude, latitude) centroid of the polygon."""
        try:
            centroid = Polygon(coordinates).centroid
            return (centroid.x, centroid.y)
        except Exception as exc:
            raise SpatialOperationException(f"Failed to calculate centroid: {exc}") from exc

    def simplify_polygon(
        self,
        coordinates: List[Tuple[float, float]],
        tolerance: float = 0.0001,
    ) -> List[Tuple[float, float]]:
        """
        Douglas-Peucker simplification of a polygon boundary.

        Args:
            tolerance: Simplification tolerance in degrees (default 0.0001 ≈ 11 m).

        Returns:
            Simplified coordinates (closed ring).
        """
        try:
            simplified = Polygon(coordinates).simplify(tolerance, preserve_topology=True)
            coords = list(simplified.exterior.coords)
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            return coords
        except Exception as exc:
            raise SpatialOperationException(f"Failed to simplify polygon: {exc}") from exc

    # ------------------------------------------------------------------
    # Overlap / intersection / containment
    # ------------------------------------------------------------------

    def polygons_overlap(
        self,
        coords_a: List[Tuple[float, float]],
        coords_b: List[Tuple[float, float]],
    ) -> bool:
        """Return True when the two polygons share any area (not merely touch at an edge/corner)."""
        try:
            poly_a = Polygon(coords_a)
            poly_b = Polygon(coords_b)
            # Use positive intersection area; intersects() is True for boundary touches too
            return poly_a.intersection(poly_b).area > 0
        except Exception as exc:
            raise SpatialOperationException(f"Failed to check overlap: {exc}") from exc

    def calculate_overlap_area(
        self,
        coords_a: List[Tuple[float, float]],
        coords_b: List[Tuple[float, float]],
    ) -> float:
        """
        Return the geodesic overlap area in **square metres**.

        Returns 0.0 when the polygons do not intersect.
        """
        try:
            poly_a = Polygon(coords_a)
            poly_b = Polygon(coords_b)
            intersection = poly_a.intersection(poly_b)
            if intersection.is_empty:
                return 0.0
            area, _ = self.geod.geometry_area_perimeter(intersection)
            return abs(area)
        except Exception as exc:
            raise SpatialOperationException(f"Failed to calculate overlap area: {exc}") from exc

    def get_overlap_percentage(
        self,
        coords_a: List[Tuple[float, float]],
        coords_b: List[Tuple[float, float]],
    ) -> float:
        """
        Return what percentage of polygon A is covered by polygon B (0–100).
        """
        area_a = self.calculate_area(coords_a)
        if area_a == 0:
            return 0.0
        overlap = self.calculate_overlap_area(coords_a, coords_b)
        return min((overlap / area_a) * 100, 100.0)

    def polygon_contains_point(
        self,
        coordinates: List[Tuple[float, float]],
        point: Tuple[float, float],
    ) -> bool:
        """Return True when *point* (lon, lat) lies inside the polygon."""
        try:
            return Polygon(coordinates).contains(Point(point[0], point[1]))
        except Exception as exc:
            raise SpatialOperationException(f"Failed to check point containment: {exc}") from exc

    def polygon_contains_polygon(
        self,
        outer_coords: List[Tuple[float, float]],
        inner_coords: List[Tuple[float, float]],
    ) -> bool:
        """Return True when *inner* polygon is fully contained within *outer*."""
        try:
            return Polygon(outer_coords).contains(Polygon(inner_coords))
        except Exception as exc:
            raise SpatialOperationException(f"Failed to check polygon containment: {exc}") from exc

    # ------------------------------------------------------------------
    # Boundary checks
    # ------------------------------------------------------------------

    def get_bounding_box(
        self, coordinates: List[Tuple[float, float]]
    ) -> Dict[str, float]:
        """
        Return the axis-aligned bounding box of the polygon.

        Returns:
            {min_lon, min_lat, max_lon, max_lat}
        """
        try:
            bounds = Polygon(coordinates).bounds  # (minx, miny, maxx, maxy)
            return {
                "min_lon": bounds[0],
                "min_lat": bounds[1],
                "max_lon": bounds[2],
                "max_lat": bounds[3],
            }
        except Exception as exc:
            raise SpatialOperationException(f"Failed to get bounding box: {exc}") from exc

    def merge_polygons(
        self, polygon_list: List[List[Tuple[float, float]]]
    ) -> List[Tuple[float, float]]:
        """
        Union a list of polygons into a single merged boundary.

        Returns the exterior ring of the resulting polygon (or convex hull
        for multi-part results).
        """
        try:
            polys = [Polygon(c) for c in polygon_list]
            merged = unary_union(polys)
            if isinstance(merged, MultiPolygon):
                merged = merged.convex_hull
            coords = list(merged.exterior.coords)
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            return coords
        except Exception as exc:
            raise SpatialOperationException(f"Failed to merge polygons: {exc}") from exc

    def buffer_polygon(
        self,
        coordinates: List[Tuple[float, float]],
        distance_degrees: float = 0.0001,
    ) -> List[Tuple[float, float]]:
        """
        Return a polygon expanded by *distance_degrees* on all sides.

        Note: degree-based buffer; for metre accuracy convert using
        ≈ 0.00001° ≈ 1 m at Ethiopian latitudes.
        """
        try:
            buffered = Polygon(coordinates).buffer(distance_degrees)
            coords = list(buffered.exterior.coords)
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            return coords
        except Exception as exc:
            raise SpatialOperationException(f"Failed to buffer polygon: {exc}") from exc

    # ------------------------------------------------------------------
    # WKT / GeoJSON helpers
    # ------------------------------------------------------------------

    def create_wkt_polygon(self, coordinates: List[Tuple[float, float]]) -> str:
        """
        Create a ``SRID=4326;POLYGON(…)`` WKT string for PostGIS storage.
        """
        try:
            return f"SRID=4326;{Polygon(coordinates).wkt}"
        except Exception as exc:
            raise SpatialOperationException(f"Failed to create WKT polygon: {exc}") from exc

    @staticmethod
    def coordinates_to_geojson(
        coordinates: List[Tuple[float, float]],
    ) -> Dict:
        """Return a GeoJSON *Polygon* feature dict for the given coordinates."""
        try:
            return mapping(Polygon(coordinates))
        except Exception as exc:
            raise SpatialOperationException(f"Failed to convert to GeoJSON: {exc}") from exc

    @staticmethod
    def geojson_to_coordinates(geojson: Dict) -> List[Tuple[float, float]]:
        """Extract the exterior ring coordinates from a GeoJSON Polygon."""
        try:
            poly = shape(geojson)
            return list(poly.exterior.coords)
        except Exception as exc:
            raise SpatialOperationException(f"Failed to parse GeoJSON: {exc}") from exc

    # ------------------------------------------------------------------
    # Spatial summary (for valuation context)
    # ------------------------------------------------------------------

    def get_spatial_summary(self, coordinates: List[Tuple[float, float]]) -> Dict:
        """
        Return a dict with all key spatial metrics for a property boundary.

        Useful as input to the valuation service or certificate generation.
        """
        area_sqm     = self.calculate_area(coordinates)
        perimeter_m  = self.calculate_perimeter(coordinates)
        centroid     = self.get_polygon_centroid(coordinates)
        bbox         = self.get_bounding_box(coordinates)
        in_ethiopia  = self.validate_ethiopian_coordinates(coordinates)

        return {
            "area_sqm":         round(area_sqm, 2),
            "area_hectares":    round(area_sqm / 10_000, 4),
            "area_acres":       round(area_sqm / 4_046.856, 4),
            "perimeter_m":      round(perimeter_m, 2),
            "centroid_lon":     round(centroid[0], 6),
            "centroid_lat":     round(centroid[1], 6),
            "bounding_box":     bbox,
            "in_ethiopia":      in_ethiopia,
            "vertex_count":     len(coordinates),
        }
