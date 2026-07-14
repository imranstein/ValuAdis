import 'dart:math';

/// Meters per degree of latitude. A degree of longitude is scaled by
/// cos(latitude) in [polygonAreaSqm] below to account for meridian convergence.
const double _metersPerDegree = 111320.0;

/// Computes the planar area of a lat/lng polygon in square meters using an
/// equirectangular projection referenced at the polygon's mean latitude.
///
/// [ring] is a list of `[longitude, latitude]` pairs. The ring is always
/// treated as closed: the final vertex is joined back to the first, so callers
/// may pass an open ring. A repeated closing vertex (as produced by WKT) is
/// dropped first so it does not skew the reference latitude. Returns 0 for
/// degenerate input (fewer than three distinct vertices).
double polygonAreaSqm(List<List<double>> ring) {
  final points = _openRing(ring);
  if (points.length < 3) return 0.0;

  final meanLatRad =
      points.map((p) => p[1]).reduce((a, b) => a + b) /
          points.length *
          (pi / 180.0);
  final cosLat = cos(meanLatRad);

  // Shoelace over the closed ring. Closing the ring is essential: without the
  // final vertex-to-first edge the absolute lon*lat cross terms never cancel,
  // inflating the result by several orders of magnitude.
  double sum = 0.0;
  for (var i = 0; i < points.length; i++) {
    final current = points[i];
    final next = points[(i + 1) % points.length];
    final x1 = current[0] * _metersPerDegree * cosLat;
    final y1 = current[1] * _metersPerDegree;
    final x2 = next[0] * _metersPerDegree * cosLat;
    final y2 = next[1] * _metersPerDegree;
    sum += x1 * y2 - x2 * y1;
  }
  return sum.abs() / 2.0;
}

/// Parses a WKT `POLYGON((lng lat, lng lat, ...))` string into a list of
/// `[longitude, latitude]` pairs for the backend `coordinates` field.
///
/// Returns an empty list when [wkt] is null or is not a POLYGON. The closing
/// duplicate vertex present in valid WKT is preserved.
List<List<double>> parseWktPolygon(String? wkt) {
  if (wkt == null) return const [];
  final match =
      RegExp(r'POLYGON\s*\(\((.*)\)\)', caseSensitive: false).firstMatch(wkt);
  if (match == null) return const [];

  final coordinates = <List<double>>[];
  for (final pair in match.group(1)!.split(',')) {
    final parts = pair.trim().split(RegExp(r'\s+'));
    if (parts.length < 2) continue;
    final lng = double.tryParse(parts[0]);
    final lat = double.tryParse(parts[1]);
    if (lng == null || lat == null) continue;
    coordinates.add([lng, lat]);
  }
  return coordinates;
}

/// Drops a trailing vertex that repeats the first one (a closed WKT ring) so the
/// shoelace and mean-latitude calculations see each vertex exactly once.
List<List<double>> _openRing(List<List<double>> ring) {
  if (ring.length >= 2) {
    final first = ring.first;
    final last = ring.last;
    if (first[0] == last[0] && first[1] == last[1]) {
      return ring.sublist(0, ring.length - 1);
    }
  }
  return ring;
}
