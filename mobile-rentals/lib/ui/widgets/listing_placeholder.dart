import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../l10n/app_localizations.dart';

/// Honest imagery for the photography-forward card. Shown only when a listing
/// has no real uploaded photos yet, so rather than fake a stock photo of a real
/// unit, this renders a deterministic brand-tinted gradient keyed to the listing
/// id, with a property-type glyph and a quiet "Photo pending" note. It reads as a
/// designed placeholder, never as the actual home. See DESIGN.md section 4.
class ListingPlaceholder extends StatelessWidget {
  const ListingPlaceholder({
    super.key,
    required this.seed,
    required this.propertySubtype,
    this.showNote = true,
  });

  final String seed;
  final String? propertySubtype;
  final bool showNote;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final hash = seed.codeUnits.fold<int>(7, (a, b) => (a * 31 + b) & 0xffffff);
    final begin = Alignment(-1 + (hash % 7) / 6, -1);
    final tint = (hash >> 3) % 3;
    final gradientColors = switch (tint) {
      0 => [c.greenDeep, c.green, c.greenLight],
      1 => [c.green, c.greenLight, c.gold.withValues(alpha: 0.65)],
      _ => [c.greenDeep, c.green, c.gold.withValues(alpha: 0.5)],
    };

    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: begin,
          end: Alignment.bottomRight,
          colors: gradientColors,
        ),
      ),
      child: Stack(
        children: [
          // Faint architectural motif so the surface is not a flat block.
          Positioned.fill(
            child: CustomPaint(painter: _MotifPainter(c.onGreen)),
          ),
          Center(
            child: Icon(_glyph(propertySubtype),
                size: 40, color: c.onGreen.withValues(alpha: 0.85)),
          ),
          if (showNote)
            Positioned(
              left: 12,
              bottom: 10,
              child: Row(
                children: [
                  Icon(Icons.photo_camera_back_outlined,
                      size: 12, color: c.onGreen.withValues(alpha: 0.75)),
                  const SizedBox(width: 4),
                  Text(
                      AppLocalizations.of(context)?.photoPendingLabel ??
                          'Photo pending',
                      style: AppType.caption(c,
                          color: c.onGreen.withValues(alpha: 0.75))),
                ],
              ),
            ),
        ],
      ),
    );
  }

  IconData _glyph(String? subtype) {
    switch (subtype) {
      case 'villa':
      case 'single_family':
      case 'townhouse':
        return Icons.house_outlined;
      case 'studio':
        return Icons.meeting_room_outlined;
      case 'condominium':
      case 'apartment':
      default:
        return Icons.apartment_outlined;
    }
  }
}

class _MotifPainter extends CustomPainter {
  _MotifPainter(this.color);
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withValues(alpha: 0.05)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    for (double x = size.width * 0.5; x < size.width * 1.4; x += 26) {
      canvas.drawLine(Offset(x, 0), Offset(x - size.height, size.height), paint);
    }
  }

  @override
  bool shouldRepaint(_MotifPainter oldDelegate) => oldDelegate.color != color;
}
