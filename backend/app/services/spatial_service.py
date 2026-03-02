"""
Spatial Service

PostGIS spatial operations and GPS coordinate processing for ValuAdis
"""

from typing import List, Tuple
from shapely.geometry import Polygon
from shapely import wkt
from pyproj import Geod
from app.core.exceptions import SpatialOperationException


class SpatialService:
    def __init__(self):
        self.geod = Geod(ellps="WGS84")
    
    def validate_polygon(self, coordinates: List[Tuple[float, float]]) -> bool:
        """
        Validate GPS coordinates form a valid polygon
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            
        Returns:
            True if valid polygon, False otherwise
        """
        if not coordinates or len(coordinates) < 4:
            return False  # Need at least 3 vertices + closing point
        
        # Check if polygon is closed (first == last)
        if coordinates[0] != coordinates[-1]:
            return False
        
        # Check if all coordinates are valid
        for lon, lat in coordinates:
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                return False
        
        try:
            # Create Shapely polygon and validate
            polygon = Polygon(coordinates)
            return polygon.is_valid and not polygon.is_empty
        except Exception:
            return False
    
    def calculate_area(self, coordinates: List[Tuple[float, float]]) -> float:
        """
        Calculate area in square meters using geodesic calculation
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            
        Returns:
            Area in square meters
        """
        try:
            polygon = Polygon(coordinates)
            area, _ = self.geod.geometry_area_perimeter(polygon)
            return abs(area)  # Return positive area
        except Exception as e:
            raise SpatialOperationException(f"Failed to calculate area: {str(e)}")
    
    def create_wkt_polygon(self, coordinates: List[Tuple[float, float]]) -> str:
        """
        Create WKT polygon string for PostGIS storage
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            
        Returns:
            WKT polygon string with SRID 4326
        """
        try:
            polygon = Polygon(coordinates)
            return f"SRID=4326;{polygon.wkt}"
        except Exception as e:
            raise SpatialOperationException(f"Failed to create WKT polygon: {str(e)}")
    
    def calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two points in meters
        
        Args:
            point1: (longitude, latitude) of first point
            point2: (longitude, latitude) of second point
            
        Returns:
            Distance in meters
        """
        try:
            _, _, distance = self.geod.inv(point1[0], point1[1], point2[0], point2[1])
            return abs(distance)
        except Exception as e:
            raise SpatialOperationException(f"Failed to calculate distance: {str(e)}")
    
    def validate_ethiopian_coordinates(self, coordinates: List[Tuple[float, float]]) -> bool:
        """
        Validate coordinates are within Ethiopia bounds
        
        Ethiopia approximate bounds:
        - Longitude: 33°E to 48°E
        - Latitude: 3°N to 15°N
        """
        for lon, lat in coordinates:
            if not (33 <= lon <= 48) or not (3 <= lat <= 15):
                return False
        return True
    
    def simplify_polygon(
        self,
        coordinates: List[Tuple[float, float]],
        tolerance: float = 0.0001
    ) -> List[Tuple[float, float]]:
        """
        Simplify polygon to reduce number of vertices
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            tolerance: Simplification tolerance in degrees
            
        Returns:
            Simplified coordinates
        """
        try:
            polygon = Polygon(coordinates)
            simplified = polygon.simplify(tolerance, preserve_topology=True)
            
            # Convert back to list of coordinates
            coords = list(simplified.exterior.coords)
            
            # Ensure polygon is closed
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            
            return coords
        except Exception as e:
            raise SpatialOperationException(f"Failed to simplify polygon: {str(e)}")
    
    def get_polygon_centroid(self, coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Get centroid of polygon
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            
        Returns:
            Centroid coordinates (longitude, latitude)
        """
        try:
            polygon = Polygon(coordinates)
            centroid = polygon.centroid
            return (centroid.x, centroid.y)
        except Exception as e:
            raise SpatialOperationException(f"Failed to calculate centroid: {str(e)}")
