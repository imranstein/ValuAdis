"""
Spatial Service Tests

Unit tests for SpatialService covering polygon validation, area / perimeter
calculations, overlap detection, merging, GeoJSON conversion, and spatial
summaries.

All test polygons lie within Ethiopia's bounding box (33°–48°E, 3°–15°N).
"""

import pytest

from app.core.exceptions import SpatialOperationException
from app.services.spatial_service import SpatialService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc() -> SpatialService:
    return SpatialService()


# ---------------------------------------------------------------------------
# Helper polygons (within Ethiopia)
# ---------------------------------------------------------------------------

# 1° × 1° square near Addis Ababa
SQUARE_A = [[38.0, 9.0], [39.0, 9.0], [39.0, 10.0], [38.0, 10.0], [38.0, 9.0]]

# Partially overlapping square (offset by 0.5° NE)
SQUARE_B_OVERLAP = [[38.5, 9.5], [39.5, 9.5], [39.5, 10.5], [38.5, 10.5], [38.5, 9.5]]

# Entirely separate square (no shared boundary with SQUARE_A)
SQUARE_C_NO_OVERLAP = [[40.5, 9.0], [41.5, 9.0], [41.5, 10.0], [40.5, 10.0], [40.5, 9.0]]

# Shares only the lon=39 edge with SQUARE_A (touching, no area overlap)
SQUARE_D_EDGE_ONLY = [[39.0, 9.0], [40.0, 9.0], [40.0, 10.0], [39.0, 10.0], [39.0, 9.0]]

# Fully inside SQUARE_A
SQUARE_E_INNER = [[38.2, 9.2], [38.8, 9.2], [38.8, 9.8], [38.2, 9.8], [38.2, 9.2]]

# A small triangle (minimum polygon) inside Ethiopia
TRIANGLE = [[35.0, 5.0], [36.0, 5.0], [35.5, 6.0], [35.0, 5.0]]


# ---------------------------------------------------------------------------
# Polygon validation
# ---------------------------------------------------------------------------

class TestPolygonValidation:
    def test_valid_closed_polygon_returns_true(self, svc):
        assert svc.validate_polygon(SQUARE_A) is True

    def test_valid_triangle_returns_true(self, svc):
        assert svc.validate_polygon(TRIANGLE) is True

    def test_open_polygon_returns_false(self, svc):
        open_poly = [[38.0, 9.0], [39.0, 9.0], [39.0, 10.0], [38.0, 10.0]]
        assert svc.validate_polygon(open_poly) is False

    def test_too_few_points_returns_false(self, svc):
        # Only 3 points (needs ≥ 4)
        assert svc.validate_polygon([[38.0, 9.0], [39.0, 9.0], [38.0, 9.0]]) is False

    def test_empty_list_returns_false(self, svc):
        assert svc.validate_polygon([]) is False

    def test_out_of_range_longitude_returns_false(self, svc):
        bad = [[200.0, 9.0], [201.0, 9.0], [201.0, 10.0], [200.0, 10.0], [200.0, 9.0]]
        assert svc.validate_polygon(bad) is False

    def test_out_of_range_latitude_returns_false(self, svc):
        bad = [[38.0, 95.0], [39.0, 95.0], [39.0, 96.0], [38.0, 96.0], [38.0, 95.0]]
        assert svc.validate_polygon(bad) is False


class TestEthiopianCoordinatesValidation:
    def test_coordinates_inside_ethiopia_returns_true(self, svc):
        assert svc.validate_ethiopian_coordinates(SQUARE_A) is True

    def test_coordinates_outside_ethiopia_returns_false(self, svc):
        # Outside — over the Atlantic Ocean
        outside = [[0.0, 9.0], [1.0, 9.0], [1.0, 10.0], [0.0, 10.0], [0.0, 9.0]]
        assert svc.validate_ethiopian_coordinates(outside) is False

    def test_partial_outside_returns_false(self, svc):
        # One point east of 48° E
        mixed = [[38.0, 9.0], [50.0, 9.0], [50.0, 10.0], [38.0, 10.0], [38.0, 9.0]]
        assert svc.validate_ethiopian_coordinates(mixed) is False


# ---------------------------------------------------------------------------
# Area calculations
# ---------------------------------------------------------------------------

class TestAreaCalculations:
    def test_area_positive(self, svc):
        assert svc.calculate_area(SQUARE_A) > 0

    def test_area_hectares_smaller_than_sqm(self, svc):
        assert svc.calculate_area_hectares(SQUARE_A) == svc.calculate_area(SQUARE_A) / 10_000

    def test_area_acres_correct_conversion(self, svc):
        assert pytest.approx(
            svc.calculate_area_acres(SQUARE_A), rel=1e-5
        ) == svc.calculate_area(SQUARE_A) / 4_046.856

    def test_larger_polygon_larger_area(self, svc):
        # SQUARE_A is 1°×1°; SQUARE_E_INNER is ~0.6°×0.6° so smaller
        assert svc.calculate_area(SQUARE_A) > svc.calculate_area(SQUARE_E_INNER)

    def test_area_raises_for_degenerate_polygon(self, svc):
        # Line (all same latitude) — not a valid polygon but should raise
        with pytest.raises(SpatialOperationException):
            svc.calculate_area([[38.0, 9.0], [39.0, 9.0]])


# ---------------------------------------------------------------------------
# Perimeter calculations
# ---------------------------------------------------------------------------

class TestPerimeterCalculations:
    def test_perimeter_positive(self, svc):
        assert svc.calculate_perimeter(SQUARE_A) > 0

    def test_perimeter_larger_for_bigger_polygon(self, svc):
        assert svc.calculate_perimeter(SQUARE_A) > svc.calculate_perimeter(SQUARE_E_INNER)

    def test_perimeter_same_whether_open_or_closed(self, svc):
        # The method closes the ring internally if it is open
        closed = SQUARE_A
        open_poly = SQUARE_A[:-1]   # remove closing point
        assert pytest.approx(
            svc.calculate_perimeter(closed), rel=1e-6
        ) == svc.calculate_perimeter(open_poly)


# ---------------------------------------------------------------------------
# Centroid and bounding box
# ---------------------------------------------------------------------------

class TestCentroidAndBoundingBox:
    def test_centroid_inside_polygon(self, svc):
        lon, lat = svc.get_polygon_centroid(SQUARE_A)
        # SQUARE_A covers 38–39 lon, 9–10 lat; centroid should be ~(38.5, 9.5)
        assert pytest.approx(lon, abs=0.01) == 38.5
        assert pytest.approx(lat, abs=0.01) == 9.5

    def test_bounding_box_keys(self, svc):
        bb = svc.get_bounding_box(SQUARE_A)
        assert set(bb.keys()) == {"min_lon", "min_lat", "max_lon", "max_lat"}

    def test_bounding_box_values_correct(self, svc):
        bb = svc.get_bounding_box(SQUARE_A)
        assert pytest.approx(bb["min_lon"]) == 38.0
        assert pytest.approx(bb["max_lon"]) == 39.0
        assert pytest.approx(bb["min_lat"]) == 9.0
        assert pytest.approx(bb["max_lat"]) == 10.0


# ---------------------------------------------------------------------------
# Overlap detection (area-based — edge touches must be False)
# ---------------------------------------------------------------------------

class TestPolygonsOverlap:
    def test_overlapping_polygons_true(self, svc):
        assert svc.polygons_overlap(SQUARE_A, SQUARE_B_OVERLAP) is True

    def test_non_overlapping_polygons_false(self, svc):
        assert svc.polygons_overlap(SQUARE_A, SQUARE_C_NO_OVERLAP) is False

    def test_edge_touch_only_is_false(self, svc):
        # SQUARE_D shares only the lon=39 edge — intersection is a LineString (area=0)
        assert svc.polygons_overlap(SQUARE_A, SQUARE_D_EDGE_ONLY) is False

    def test_contained_polygon_is_overlap(self, svc):
        assert svc.polygons_overlap(SQUARE_A, SQUARE_E_INNER) is True

    def test_polygon_overlaps_with_itself(self, svc):
        assert svc.polygons_overlap(SQUARE_A, SQUARE_A) is True


# ---------------------------------------------------------------------------
# Overlap area
# ---------------------------------------------------------------------------

class TestOverlapArea:
    def test_no_overlap_returns_zero(self, svc):
        assert svc.calculate_overlap_area(SQUARE_A, SQUARE_C_NO_OVERLAP) == 0.0

    def test_edge_touch_returns_zero(self, svc):
        assert svc.calculate_overlap_area(SQUARE_A, SQUARE_D_EDGE_ONLY) == 0.0

    def test_overlapping_area_is_positive(self, svc):
        assert svc.calculate_overlap_area(SQUARE_A, SQUARE_B_OVERLAP) > 0.0

    def test_contained_polygon_overlap_equals_inner_area(self, svc):
        inner_area   = svc.calculate_area(SQUARE_E_INNER)
        overlap_area = svc.calculate_overlap_area(SQUARE_A, SQUARE_E_INNER)
        assert pytest.approx(overlap_area, rel=1e-4) == inner_area

    def test_overlap_percentage_zero_for_non_overlapping(self, svc):
        assert svc.get_overlap_percentage(SQUARE_A, SQUARE_C_NO_OVERLAP) == 0.0

    def test_overlap_percentage_100_when_fully_contained(self, svc):
        # SQUARE_E is entirely inside SQUARE_A; % of SQUARE_E covered by SQUARE_A = 100%
        pct = svc.get_overlap_percentage(SQUARE_E_INNER, SQUARE_A)
        assert pytest.approx(pct, rel=1e-3) == 100.0

    def test_overlap_percentage_capped_at_100(self, svc):
        pct = svc.get_overlap_percentage(SQUARE_A, SQUARE_A)
        assert pct <= 100.0


# ---------------------------------------------------------------------------
# Containment
# ---------------------------------------------------------------------------

class TestContainment:
    def test_inner_polygon_contained_in_outer(self, svc):
        assert svc.polygon_contains_polygon(SQUARE_A, SQUARE_E_INNER) is True

    def test_outer_not_contained_in_inner(self, svc):
        assert svc.polygon_contains_polygon(SQUARE_E_INNER, SQUARE_A) is False

    def test_point_inside_polygon_true(self, svc):
        # Centroid of SQUARE_A ≈ (38.5, 9.5)
        assert svc.polygon_contains_point(SQUARE_A, (38.5, 9.5)) is True

    def test_point_outside_polygon_false(self, svc):
        assert svc.polygon_contains_point(SQUARE_A, (45.0, 5.0)) is False


# ---------------------------------------------------------------------------
# Merge polygons
# ---------------------------------------------------------------------------

class TestMergePolygons:
    def test_merge_two_adjacent_polygons(self, svc):
        # SQUARE_A and SQUARE_D share the lon=39 edge → single merged polygon
        merged = svc.merge_polygons([SQUARE_A, SQUARE_D_EDGE_ONLY])
        assert isinstance(merged, list)
        assert len(merged) >= 4  # at least 3 vertices + closing point

    def test_non_contiguous_raises_by_default(self, svc):
        with pytest.raises(SpatialOperationException, match="non-contiguous"):
            svc.merge_polygons([SQUARE_A, SQUARE_C_NO_OVERLAP])

    def test_non_contiguous_fallback_convex_hull_succeeds(self, svc):
        merged = svc.merge_polygons(
            [SQUARE_A, SQUARE_C_NO_OVERLAP], fallback_convex_hull=True
        )
        assert isinstance(merged, list)
        assert len(merged) >= 4

    def test_merge_single_polygon_returns_same_polygon(self, svc):
        merged = svc.merge_polygons([SQUARE_A])
        # Should be a valid closed polygon
        assert merged[0] == merged[-1]


# ---------------------------------------------------------------------------
# Buffer
# ---------------------------------------------------------------------------

class TestBufferPolygon:
    def test_buffered_polygon_larger_area(self, svc):
        buffered = svc.buffer_polygon(SQUARE_A, distance_degrees=0.1)
        assert svc.calculate_area(buffered) > svc.calculate_area(SQUARE_A)

    def test_buffered_polygon_is_closed(self, svc):
        buffered = svc.buffer_polygon(SQUARE_A)
        assert buffered[0] == buffered[-1]


# ---------------------------------------------------------------------------
# Simplification
# ---------------------------------------------------------------------------

class TestSimplifyPolygon:
    def test_simplified_polygon_fewer_or_equal_vertices(self, svc):
        simplified = svc.simplify_polygon(SQUARE_A, tolerance=0.0001)
        assert len(simplified) <= len(SQUARE_A)

    def test_simplified_polygon_is_closed(self, svc):
        simplified = svc.simplify_polygon(SQUARE_A)
        assert simplified[0] == simplified[-1]


# ---------------------------------------------------------------------------
# GeoJSON conversion
# ---------------------------------------------------------------------------

class TestGeoJsonConversion:
    def test_coordinates_to_geojson_type_is_polygon(self, svc):
        geojson = svc.coordinates_to_geojson(SQUARE_A)
        assert geojson["type"] == "Polygon"

    def test_geojson_contains_coordinates_key(self, svc):
        geojson = svc.coordinates_to_geojson(SQUARE_A)
        assert "coordinates" in geojson

    def test_geojson_round_trip_preserves_first_point(self, svc):
        geojson = svc.coordinates_to_geojson(SQUARE_A)
        back = svc.geojson_to_coordinates(geojson)
        assert pytest.approx(back[0][0], rel=1e-6) == SQUARE_A[0][0]
        assert pytest.approx(back[0][1], rel=1e-6) == SQUARE_A[0][1]

    def test_wkt_polygon_contains_srid(self, svc):
        wkt = svc.create_wkt_polygon(SQUARE_A)
        assert wkt.startswith("SRID=4326;")
        assert "POLYGON" in wkt


# ---------------------------------------------------------------------------
# Spatial summary
# ---------------------------------------------------------------------------

class TestSpatialSummary:
    _REQUIRED_KEYS = (
        "area_sqm", "area_hectares", "area_acres",
        "perimeter_m", "centroid_lon", "centroid_lat",
        "bounding_box", "in_ethiopia", "vertex_count",
    )

    def test_summary_contains_all_required_keys(self, svc):
        summary = svc.get_spatial_summary(SQUARE_A)
        for key in self._REQUIRED_KEYS:
            assert key in summary, f"Missing key: {key}"

    def test_in_ethiopia_true_for_ethiopian_polygon(self, svc):
        assert svc.get_spatial_summary(SQUARE_A)["in_ethiopia"] is True

    def test_in_ethiopia_false_for_non_ethiopian_polygon(self, svc):
        outside = [[0.0, 9.0], [1.0, 9.0], [1.0, 10.0], [0.0, 10.0], [0.0, 9.0]]
        assert svc.get_spatial_summary(outside)["in_ethiopia"] is False

    def test_area_sqm_is_positive(self, svc):
        assert svc.get_spatial_summary(SQUARE_A)["area_sqm"] > 0

    def test_area_hectares_equals_sqm_div_10000(self, svc):
        s = svc.get_spatial_summary(SQUARE_A)
        assert pytest.approx(s["area_hectares"], rel=1e-4) == s["area_sqm"] / 10_000

    def test_vertex_count_matches_input(self, svc):
        assert svc.get_spatial_summary(SQUARE_A)["vertex_count"] == len(SQUARE_A)

    def test_bounding_box_structure(self, svc):
        bb = svc.get_spatial_summary(SQUARE_A)["bounding_box"]
        assert set(bb.keys()) == {"min_lon", "min_lat", "max_lon", "max_lat"}
