import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../core/theme/motion.dart';
import '../../l10n/app_localizations.dart';
import '../widgets/brand.dart';

/// Shown while the startup session check runs. A single, calm brand moment.
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      body: Center(
        child: TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: 1),
          duration: Motion.hero,
          curve: Motion.easeOutQuint,
          builder: (context, t, child) => Opacity(
            opacity: t,
            child: Transform.translate(
                offset: Offset(0, (1 - t) * 10), child: child),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const RegistrySeal(size: 30),
              const SizedBox(height: 16),
              const BrandMark(size: 40),
              const SizedBox(height: 10),
              Text(AppLocalizations.of(context)?.splashTagline ??
                      'Government-mediated rental registry',
                  textAlign: TextAlign.center,
                  style: AppType.label(c, color: c.inkMuted)),
              const SizedBox(height: 36),
              SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                    strokeWidth: 2, valueColor: AlwaysStoppedAnimation(c.green)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
