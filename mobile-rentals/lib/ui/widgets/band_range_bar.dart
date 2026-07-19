import 'package:flutter/material.dart';

import '../../core/formatting.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/band.dart';

/// The product's core honesty gesture, visualized: the published band as a
/// horizontal track with the suggested rent marked and both bounds labeled in
/// mono ETB. Read-only display variant (the apply sheet has the interactive
/// slider). Optionally overlays [offer] as a second marker.
class BandRangeBar extends StatelessWidget {
  const BandRangeBar({
    super.key,
    required this.band,
    this.offer,
    this.showLabels = true,
  });

  final RentBand band;
  final double? offer;
  final bool showLabels;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showLabels)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Text(Fmt.rent(band.min),
                      overflow: TextOverflow.ellipsis,
                      style: AppType.mono(c,
                          size: 12,
                          weight: FontWeight.w500,
                          color: c.inkMuted)),
                ),
                const SizedBox(width: 8),
                Text('${band.spreadPercent}% band',
                    style: AppType.caption(c, color: c.inkMuted)),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(Fmt.rent(band.max),
                      textAlign: TextAlign.right,
                      overflow: TextOverflow.ellipsis,
                      style: AppType.mono(c,
                          size: 12,
                          weight: FontWeight.w500,
                          color: c.inkMuted)),
                ),
              ],
            ),
          ),
        LayoutBuilder(
          builder: (context, constraints) {
            final width = constraints.maxWidth;
            final suggestedX = band.suggestedPosition * width;
            final offerX = offer == null ? null : band.positionOf(offer!) * width;
            return SizedBox(
              height: 26,
              child: Stack(
                clipBehavior: Clip.none,
                alignment: Alignment.centerLeft,
                children: [
                  // Full track.
                  Container(
                    height: 8,
                    decoration: BoxDecoration(
                      color: c.surfaceSunken,
                      borderRadius: BorderRadius.circular(999),
                    ),
                  ),
                  // In-band fill (min → suggested), the "reasonable" zone.
                  Container(
                    height: 8,
                    width: suggestedX.clamp(6, width),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [c.greenLight, c.green],
                      ),
                      borderRadius: BorderRadius.circular(999),
                    ),
                  ),
                  // Suggested marker.
                  _marker(c, suggestedX, c.green),
                  // Offer marker (gold), when present.
                  if (offerX != null) _marker(c, offerX, c.gold),
                ],
              ),
            );
          },
        ),
        if (showLabels)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Row(
              children: [
                _dot(c, c.green),
                const SizedBox(width: 5),
                Flexible(
                  child: Text('Suggested ${Fmt.rent(band.suggested)}',
                      overflow: TextOverflow.ellipsis,
                      style: AppType.caption(c, color: c.inkSecondary)),
                ),
                if (offer != null) ...[
                  const SizedBox(width: 14),
                  _dot(c, c.gold),
                  const SizedBox(width: 5),
                  Flexible(
                    child: Text('Your offer',
                        overflow: TextOverflow.ellipsis,
                        style: AppType.caption(c, color: c.inkSecondary)),
                  ),
                ],
              ],
            ),
          ),
      ],
    );
  }

  Widget _marker(AppColors c, double x, Color color) {
    return Positioned(
      left: (x - 8).clamp(0, double.infinity),
      child: Container(
        width: 16,
        height: 16,
        decoration: BoxDecoration(
          color: c.surface,
          shape: BoxShape.circle,
          border: Border.all(color: color, width: 3),
        ),
      ),
    );
  }

  Widget _dot(AppColors c, Color color) => Container(
        width: 7,
        height: 7,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      );
}
