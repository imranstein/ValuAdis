import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import 'pressable.dart';

/// Filled green primary action. One per view. Shows an inline progress spinner
/// while [loading]; disabled state dims and blocks taps.
class PrimaryButton extends StatelessWidget {
  const PrimaryButton({
    super.key,
    required this.label,
    this.onPressed,
    this.loading = false,
    this.icon,
    this.expand = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool loading;
  final IconData? icon;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final enabled = onPressed != null && !loading;
    final child = Container(
      height: 52,
      width: expand ? double.infinity : null,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: enabled ? c.green : c.green.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(14),
      ),
      child: loading
          ? SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2.2,
                valueColor: AlwaysStoppedAnimation(c.onGreen),
              ),
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: 19, color: c.onGreen),
                  const SizedBox(width: 8),
                ],
                Text(label,
                    style: AppType.label(c,
                        color: c.onGreen, weight: FontWeight.w600)),
              ],
            ),
    );
    return Pressable(onTap: enabled ? onPressed : null, child: child);
  }
}

/// Tonal secondary action: green text on a soft tint, no fill weight.
class GhostButton extends StatelessWidget {
  const GhostButton({
    super.key,
    required this.label,
    this.onPressed,
    this.icon,
    this.danger = false,
    this.expand = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool danger;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final tint = danger ? c.danger : c.green;
    final child = Container(
      height: 50,
      width: expand ? double.infinity : null,
      padding: const EdgeInsets.symmetric(horizontal: 20),
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: (danger ? c.dangerWash : c.greenSoft).withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: tint.withValues(alpha: 0.28)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 18, color: tint),
            const SizedBox(width: 8),
          ],
          Text(label,
              style: AppType.label(c, color: tint, weight: FontWeight.w600)),
        ],
      ),
    );
    return Pressable(onTap: onPressed, child: child);
  }
}
