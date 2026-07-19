import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/registry_status.dart';

/// Status pill: tonal wash + dot + label, consistent across applications,
/// listings, and contracts. Tone comes from the centralised [RegistryStatus].
class StatusPill extends StatelessWidget {
  const StatusPill(this.rawStatus, {super.key, this.compact = false});

  final String rawStatus;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final kind = RegistryStatus.kindOf(rawStatus);
    final (fg, bg) = _colors(c, kind);
    return Container(
      padding: EdgeInsets.symmetric(
          horizontal: compact ? 8 : 10, vertical: compact ? 4 : 5),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: fg, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text(RegistryStatus.labelOf(rawStatus),
              style: AppType.caption(c, color: fg)
                  .copyWith(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  (Color, Color) _colors(AppColors c, StatusKind kind) {
    switch (kind) {
      case StatusKind.positive:
        return (c.green, c.greenSoft);
      case StatusKind.pending:
        return (c.gold, c.goldWash);
      case StatusKind.negative:
        return (c.danger, c.dangerWash);
      case StatusKind.neutral:
        return (c.inkMuted, c.surfaceSunken);
    }
  }
}

/// The trust mark. Only shown when a listing genuinely carries a valuation
/// certificate; never decorative.
class CertifiedBadge extends StatelessWidget {
  const CertifiedBadge({super.key, this.onDark = false});
  final bool onDark;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: onDark ? Colors.black.withValues(alpha: 0.42) : c.goldWash,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: c.gold.withValues(alpha: 0.55)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.verified_outlined,
              size: 13, color: onDark ? c.gold : c.gold),
          const SizedBox(width: 5),
          Text('Certified',
              style: AppType.caption(c, color: onDark ? c.gold : c.gold)
                  .copyWith(fontWeight: FontWeight.w700, letterSpacing: 0.4)),
        ],
      ),
    );
  }
}

/// Small icon + value chip for compact property facts (beds, baths, area).
class MetaChip extends StatelessWidget {
  const MetaChip({super.key, required this.icon, required this.label});
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 15, color: c.inkMuted),
        const SizedBox(width: 5),
        Text(label, style: AppType.label(c, color: c.inkSecondary)),
      ],
    );
  }
}
