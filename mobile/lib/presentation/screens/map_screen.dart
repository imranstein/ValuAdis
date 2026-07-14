import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../core/constants.dart';
import '../../core/geo.dart';
import '../theme/app_theme.dart';
import '../widgets/shared_ui.dart';

class MapScreen extends StatefulWidget {
  final bool showAppBar;

  const MapScreen({
    super.key,
    this.showAppBar = true,
  });

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final List<LatLng> _points = [];
  final MapController _mapController = MapController();
  double _calculatedArea = 0.0;

  void _handleMapTap(TapPosition position, LatLng latlng) {
    setState(() {
      _points.add(latlng);
      if (_points.length >= 3) {
        _calculatedArea = _calculateArea(_points);
      }
    });
  }

  void _clearPoints() {
    setState(() {
      _points.clear();
      _calculatedArea = 0.0;
    });
  }

  void _complete() {
    if (_points.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Add at least 3 points to form a boundary'),
        ),
      );
      return;
    }
    final closed = List<LatLng>.from(_points)..add(_points.first);
    final wkt = _toWkt(closed);
    Navigator.of(
      context,
    ).pop(MapScreenResult(wkt: wkt, areaSqm: _calculatedArea));
  }

  String _toWkt(List<LatLng> pts) {
    final coords = pts.map((p) => '${p.longitude} ${p.latitude}').join(', ');
    return 'POLYGON(($coords))';
  }

  double _calculateArea(List<LatLng> points) {
    return polygonAreaSqm(
      points.map((p) => [p.longitude, p.latitude]).toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Column(
        children: [
          if (widget.showAppBar)
            AppBar(
              title: const Text('Draw boundary'),
              actions: [
                if (_points.isNotEmpty)
                  TextButton(onPressed: _clearPoints, child: const Text('Clear')),
              ],
            ),
          Expanded(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: const LatLng(
                  AppConstants.defaultMapLat,
                  AppConstants.defaultMapLon,
                ),
                initialZoom: AppConstants.defaultMapZoom,
                onTap: _handleMapTap,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                ),
                if (_points.length > 1)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: _points.length >= 3
                            ? [..._points, _points.first]
                            : _points,
                        strokeWidth: 3,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ],
                  ),
                MarkerLayer(
                  markers: _points
                      .map(
                        (p) => Marker(
                          point: p,
                          width: AppSpacing.lg,
                          height: AppSpacing.lg,
                          child: Icon(
                            Icons.location_on,
                            color: Theme.of(context).colorScheme.error,
                            size: AppSpacing.lg,
                          ),
                        ),
                      )
                      .toList(),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(AppSpacing.md),
            color: Theme.of(context).colorScheme.surface,
            child: Column(
              children: [
                if (_points.isEmpty)
                  const AppEmptyState(
                    icon: Icons.route,
                    title: 'Add boundary points',
                    message: 'Tap the map to add at least 3 points.',
                  )
                else
                  Text(
                    'Points: ${_points.length} (min 3)',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                if (_calculatedArea > 0)
                  Padding(
                    padding: const EdgeInsets.only(top: AppSpacing.xs),
                    child: Text(
                      'Area: ${_calculatedArea.toStringAsFixed(2)} sqm',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                const SizedBox(height: AppSpacing.md),
                if (_points.isNotEmpty)
                  OutlinedButton(
                    onPressed: _clearPoints,
                    child: const Text('Clear'),
                  ),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: _points.length >= 3 ? _complete : null,
                    child: const Text('Done'),
                  ),
                ),
                if (!widget.showAppBar)
                  const SizedBox(height: AppSpacing.md),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class MapScreenResult {
  final String? wkt;
  final double areaSqm;

  MapScreenResult({this.wkt, this.areaSqm = 0});
}
