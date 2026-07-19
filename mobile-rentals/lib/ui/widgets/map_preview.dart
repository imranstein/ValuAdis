import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../l10n/app_localizations.dart';

/// A non-interactive location preview. When coordinates are missing it shows an
/// honest "location not pinned" placeholder rather than a misleading default pin.
class MapPreview extends StatelessWidget {
  const MapPreview({
    super.key,
    required this.latitude,
    required this.longitude,
    this.height = 180,
    this.interactive = false,
  });

  final double? latitude;
  final double? longitude;
  final double height;
  final bool interactive;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    if (latitude == null || longitude == null) {
      return Container(
        height: height,
        decoration: BoxDecoration(
          color: c.surfaceSunken,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: c.border),
        ),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.location_off_outlined, color: c.inkMuted, size: 26),
              const SizedBox(height: 6),
              Text(
                  AppLocalizations.of(context)?.locationNotPinnedLabel ??
                      'Location not pinned',
                  style: AppType.label(c, color: c.inkMuted)),
            ],
          ),
        ),
      );
    }

    final point = LatLng(latitude!, longitude!);
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: SizedBox(
        height: height,
        child: FlutterMap(
          options: MapOptions(
            initialCenter: point,
            initialZoom: 15,
            interactionOptions: InteractionOptions(
              flags: interactive ? InteractiveFlag.all : InteractiveFlag.none,
            ),
          ),
          children: [
            TileLayer(
              urlTemplate:
                  'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.valuadis.rent',
            ),
            MarkerLayer(
              markers: [
                Marker(
                  point: point,
                  width: 40,
                  height: 40,
                  child: Icon(Icons.location_on,
                      color: c.green, size: 36),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
