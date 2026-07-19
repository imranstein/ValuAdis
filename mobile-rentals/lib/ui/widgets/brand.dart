import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';

/// The wordmark: serif "ValuAdis" with a gold "Rent" — the app's one brand
/// moment, used on welcome, auth, and the app bar leading slot.
class BrandMark extends StatelessWidget {
  const BrandMark({super.key, this.size = 30, this.color});
  final double size;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return RichText(
      text: TextSpan(
        style: AppType.serifDisplay(c, size: size, color: color ?? c.ink),
        children: [
          const TextSpan(text: 'ValuAdis '),
          TextSpan(
            text: 'Rent',
            style: AppType.serifDisplay(c,
                size: size, weight: FontWeight.w600, color: c.gold),
          ),
        ],
      ),
    );
  }
}

/// A small seal used beside official-register copy.
class RegistrySeal extends StatelessWidget {
  const RegistrySeal({super.key, this.size = 18});
  final double size;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Icon(Icons.account_balance_outlined, size: size, color: c.green);
  }
}
