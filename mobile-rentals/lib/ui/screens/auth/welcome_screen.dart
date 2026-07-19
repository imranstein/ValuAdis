import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/theme/motion.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/brand.dart';
import '../../widgets/buttons.dart';
import '../../widgets/listing_placeholder.dart';
import '../../widgets/pills.dart';
import 'login_screen.dart';
import 'signup_screen.dart';

/// Brand-forward entry. Serif wordmark over a warm hero, three honest value
/// points, and a single primary path to get started.
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      backgroundColor: c.canvas,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(24, 32, 24, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const RegistrySeal(size: 20),
                        const SizedBox(width: 8),
                        Flexible(
                          child: Text(l10n.welcomeAgency,
                              style: AppType.caption(c, color: c.inkMuted)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 28),
                    const BrandMark(size: 44),
                    const SizedBox(height: 14),
                    Text(
                      l10n.welcomeHero,
                      style: AppType.body(c, color: c.inkSecondary)
                          .copyWith(fontSize: 16, height: 1.5),
                    ),
                    const SizedBox(height: 26),
                    const _HeroPreview(),
                    const SizedBox(height: 26),
                    _point(c, Icons.verified_outlined, l10n.welcomePoint1Title,
                        l10n.welcomePoint1Body),
                    _point(c, Icons.gavel_outlined, l10n.welcomePoint2Title,
                        l10n.welcomePoint2Body),
                    _point(c, Icons.insights_outlined, l10n.welcomePoint3Title,
                        l10n.welcomePoint3Body),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 20),
              child: Column(
                children: [
                  PrimaryButton(
                    label: l10n.welcomeCreateAccountCta,
                    icon: Icons.arrow_forward,
                    onPressed: () => Navigator.of(context).push(
                        MaterialPageRoute(
                            builder: (_) => const SignupScreen())),
                  ),
                  const SizedBox(height: 10),
                  GhostButton(
                    label: l10n.authAlreadyHaveAccount,
                    onPressed: () => Navigator.of(context).push(
                        MaterialPageRoute(
                            builder: (_) => const LoginScreen())),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _point(AppColors c, IconData icon, String title, String body) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
                color: c.greenSoft.withValues(alpha: 0.6),
                borderRadius: BorderRadius.circular(11)),
            child: Icon(icon, size: 19, color: c.green),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppType.headline(c).copyWith(fontSize: 16)),
                const SizedBox(height: 2),
                Text(body, style: AppType.label(c, color: c.inkMuted)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _HeroPreview extends StatelessWidget {
  const _HeroPreview();

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: Motion.hero,
      curve: Motion.easeOutQuint,
      builder: (context, t, child) => Opacity(
        opacity: t,
        child: Transform.translate(offset: Offset(0, (1 - t) * 16), child: child),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: AspectRatio(
          aspectRatio: 16 / 8,
          child: Stack(
            fit: StackFit.expand,
            children: [
              const ListingPlaceholder(
                  seed: 'welcome-hero',
                  propertySubtype: 'apartment',
                  showNote: false),
              const Positioned(top: 12, right: 12, child: CertifiedBadge(onDark: true)),
              Positioned(
                left: 14,
                bottom: 12,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.42),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                      AppLocalizations.of(context)?.welcomeHeroCaption ??
                          '28,000 ETB/mo · Bole',
                      style: AppType.mono(c,
                          size: 14,
                          weight: FontWeight.w700,
                          color: c.onGreen)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
