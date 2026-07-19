import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../core/theme/motion.dart';
import '../../l10n/app_localizations.dart';
import 'buttons.dart';

/// Composed, serif-headline empty state. Used for honest "nothing here yet"
/// surfaces (no listings match, no applications, no index data, offline).
class EmptyState extends StatelessWidget {
  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.actionLabel,
    this.onAction,
  });

  final IconData icon;
  final String title;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 76,
              height: 76,
              decoration: BoxDecoration(
                color: c.greenSoft.withValues(alpha: 0.6),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 34, color: c.green),
            ),
            const SizedBox(height: 22),
            Text(title,
                textAlign: TextAlign.center,
                style: AppType.serifDisplay(c, size: 26)),
            const SizedBox(height: 8),
            Text(message,
                textAlign: TextAlign.center,
                style: AppType.body(c, color: c.inkMuted)),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 22),
              PrimaryButton(
                  label: actionLabel!, onPressed: onAction, expand: false),
            ],
          ],
        ),
      ),
    );
  }
}

class ErrorView extends StatelessWidget {
  const ErrorView({super.key, required this.message, this.onRetry});
  final String message;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off_outlined, size: 40, color: c.inkMuted),
            const SizedBox(height: 16),
            Text(message,
                textAlign: TextAlign.center,
                style: AppType.body(c, color: c.inkSecondary)),
            if (onRetry != null) ...[
              const SizedBox(height: 20),
              GhostButton(
                  label: AppLocalizations.of(context)?.actionTryAgain ??
                      'Try again',
                  icon: Icons.refresh,
                  onPressed: onRetry,
                  expand: false),
            ],
          ],
        ),
      ),
    );
  }
}

/// Looping shimmer used by skeleton loaders. Transform/opacity only.
class Shimmer extends StatefulWidget {
  const Shimmer({super.key, required this.child});
  final Widget child;

  @override
  State<Shimmer> createState() => _ShimmerState();
}

class _ShimmerState extends State<Shimmer> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1300),
  )..repeat();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final reduce = MediaQuery.maybeOf(context)?.disableAnimations ?? false;
    if (reduce) return widget.child;
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ShaderMask(
          blendMode: BlendMode.srcATop,
          shaderCallback: (bounds) {
            final t = _controller.value;
            return LinearGradient(
              begin: Alignment(-1 - 2 * (1 - t), 0),
              end: Alignment(1 - 2 * (1 - t), 0),
              colors: [
                c.surfaceSunken,
                c.surface.withValues(alpha: 0.4),
                c.surfaceSunken,
              ],
              stops: const [0.35, 0.5, 0.65],
            ).createShader(bounds);
          },
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

Widget skeletonBox(BuildContext context,
    {double? width, double height = 14, double radius = 8}) {
  final c = AppColors.of(context);
  return Container(
    width: width,
    height: height,
    decoration: BoxDecoration(
      color: c.surfaceSunken,
      borderRadius: BorderRadius.circular(radius),
    ),
  );
}

/// Skeleton matching the [ListingCard] silhouette, so the load reads as the same
/// layout arriving rather than a spinner.
class ListingCardSkeleton extends StatelessWidget {
  const ListingCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Shimmer(
      child: Container(
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: c.border),
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AspectRatio(
                aspectRatio: 16 / 10, child: skeletonBox(context, radius: 0)),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  skeletonBox(context, width: 180, height: 16),
                  const SizedBox(height: 10),
                  skeletonBox(context, width: 120, height: 12),
                  const SizedBox(height: 18),
                  skeletonBox(context, height: 8, radius: 999),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Staggered fade+rise wrapper for list items. Reduced-motion safe.
class StaggeredReveal extends StatelessWidget {
  const StaggeredReveal({super.key, required this.index, required this.child});
  final int index;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final reduce = MediaQuery.maybeOf(context)?.disableAnimations ?? false;
    if (reduce) return child;
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: Motion.sheet + Motion.staggerFor(index),
      curve: Motion.easeOutQuint,
      builder: (context, t, child) => Opacity(
        opacity: t.clamp(0, 1),
        child: Transform.translate(offset: Offset(0, (1 - t) * 14), child: child),
      ),
      child: child,
    );
  }
}
