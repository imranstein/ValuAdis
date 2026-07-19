import 'package:flutter/material.dart';

import '../../bloc/sync/sync_state.dart';
import '../../core/utils.dart';
import '../theme/app_theme.dart';

class AppCard extends StatelessWidget {
  final Widget child;

  const AppCard({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: AppSpacing.sm),
      clipBehavior: Clip.antiAlias,
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: child,
      ),
    );
  }
}

class AppSectionHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? trailing;

  const AppSectionHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.md,
        AppSpacing.lg,
        AppSpacing.md,
        AppSpacing.sm,
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                if (subtitle != null && subtitle!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ],
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

class AppStatusChip extends StatelessWidget {
  final String label;
  final Color backgroundColor;
  final Color foregroundColor;

  const AppStatusChip({
    super.key,
    required this.label,
    required this.backgroundColor,
    required this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: AppRadius.smRadius,
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: foregroundColor,
              fontWeight: FontWeight.w600,
            ),
      ),
    );
  }

  static Color foregroundForStatus(BuildContext context, String status) {
    final colorScheme = Theme.of(context).colorScheme;
    switch (status) {
      case 'synced':
        return AppColors.success;
      case 'pending':
      case 'syncing':
        return colorScheme.primary;
      case 'failed':
        return colorScheme.error;
      default:
        return colorScheme.onSurfaceVariant;
    }
  }

  static Color backgroundForStatus(BuildContext context, String status) {
    final color = foregroundForStatus(context, status);
    return color.withOpacity(0.12);
  }

  static Widget fromStatus(
    BuildContext context,
    String status, {
    String? label,
  }) {
    final statusLabel = label ?? AppUtils.syncStatusLabel(status);
    final foreground = foregroundForStatus(context, status);
    return AppStatusChip(
      label: statusLabel,
      backgroundColor: backgroundForStatus(context, status),
      foregroundColor: foreground,
    );
  }
}

class AppEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  const AppEmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 54, color: Theme.of(context).colorScheme.outline),
            const SizedBox(height: AppSpacing.lg),
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
              textAlign: TextAlign.center,
            ),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: AppSpacing.lg),
              FilledButton(onPressed: onAction, child: Text(actionLabel!)),
            ],
          ],
        ),
      ),
    );
  }
}

class AppLoadingState extends StatelessWidget {
  final String message;

  const AppLoadingState({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: AppSpacing.md),
            Text(message),
          ],
        ),
      ),
    );
  }
}

class AppSyncBanner extends StatelessWidget {
  final SyncState syncState;

  const AppSyncBanner({
    super.key,
    required this.syncState,
  });

  @override
  Widget build(BuildContext context) {
    final shouldShow = !syncState.isOnline ||
        syncState.status == SyncStatus.syncing ||
        syncState.status == SyncStatus.synced;

    if (!shouldShow) {
      return const SizedBox.shrink();
    }

    final bannerBg = !syncState.isOnline
        ? Theme.of(context).colorScheme.error
        : syncState.status == SyncStatus.syncing
            ? Theme.of(context).colorScheme.primary
            : AppColors.success;

    final label = !syncState.isOnline
        ? 'Offline. Changes saved locally.'
        : syncState.status == SyncStatus.syncing
            ? 'Syncing pending data'
            : 'Sync complete';

    final visibleItemStatuses = syncState.itemStatuses.where(
      (entry) => entry.status == 'failed' || entry.status == 'synced',
    );

    final hasItemStatuses = visibleItemStatuses.isNotEmpty;
    final statusLines = hasItemStatuses
        ? visibleItemStatuses
            .map(
              (entry) => '${entry.scope} ${entry.id} ${entry.status} '
                  '${entry.message ?? ''}'.trim(),
            )
            .toList()
        : <String>[];

    return Material(
      color: bannerBg,
      child: SafeArea(
        top: true,
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.md,
            vertical: AppSpacing.sm,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
              ),
              if (hasItemStatuses) ...[
                const SizedBox(height: AppSpacing.xs),
                ...statusLines
                    .take(2)
                    .map(
                      (line) => Text(
                        line,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.white,
                              height: 1.2,
                            ),
                      ),
                    ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
