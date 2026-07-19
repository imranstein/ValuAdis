import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/cubits.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/application.dart';
import '../../../data/models/owner_listing.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/buttons.dart';
import '../../widgets/pills.dart';
import '../../widgets/states.dart';

class ListingApplicationsScreen extends StatelessWidget {
  const ListingApplicationsScreen({super.key, required this.listing});
  final OwnerListing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final cubit = context.read<ListingApplicationsCubit>();
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(
        title: Text(l10n.screenTitleApplications),
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 4, 20, 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(listing.propertyAddress ?? listing.publicId,
                      style: AppType.headline(c)),
                  const SizedBox(height: 4),
                  Row(children: [
                    StatusPill(listing.status),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                          l10n.bandRangeLabel(Fmt.rent(listing.band.min),
                              Fmt.rent(listing.band.max)),
                          overflow: TextOverflow.ellipsis,
                          style:
                              AppType.mono(c, size: 12, color: c.inkMuted)),
                    ),
                  ]),
                ],
              ),
            ),
            Expanded(
              child: BlocBuilder<ListingApplicationsCubit,
                  AsyncState<List<RentalApplication>>>(
                builder: (context, state) {
                  if (state.isError) {
                    return ErrorView(
                        message: state.error ?? l10n.errorLoadApplications,
                        onRetry: cubit.load);
                  }
                  if (!state.isReady) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  final apps = state.data!;
                  if (apps.isEmpty) {
                    return EmptyState(
                      icon: Icons.inbox_outlined,
                      title: l10n.emptyNoApplicationsTitle,
                      message: l10n.ownerEmptyApplicationsMessage,
                    );
                  }
                  final hasAccepted =
                      apps.any((a) => a.status.toLowerCase() == 'accepted');
                  return ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: apps.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 14),
                    itemBuilder: (context, i) => StaggeredReveal(
                      index: i,
                      child: _OwnerApplicationCard(
                        app: apps[i],
                        locked: hasAccepted,
                        onDecide: (action) =>
                            _decide(context, cubit, apps[i], action),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _decide(BuildContext context, ListingApplicationsCubit cubit,
      RentalApplication app, String action) async {
    final l10n = AppLocalizations.of(context)!;
    if (action == 'accept') {
      final confirmed = await _confirmAccept(context, app);
      if (confirmed != true) return;
    }
    final error = await cubit.decide(app.id, action);
    if (!context.mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(content: Text(error)));
    } else {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(
            content: Text(action == 'accept'
                ? l10n.snackApplicationAccepted
                : l10n.snackApplicationDeclined)));
    }
  }

  Future<bool?> _confirmAccept(BuildContext context, RentalApplication app) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: c.surface,
        title: Text(l10n.dialogAcceptTitle, style: AppType.headline(c)),
        content: Text(
          l10n.dialogAcceptContent(app.renterName ?? l10n.defaultRenterName,
              '${Fmt.rent(app.offeredRent)}${l10n.perMonthSuffixShort}'),
          style: AppType.body(c, color: c.inkSecondary),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text(l10n.actionCancel,
                  style: AppType.label(c, color: c.inkMuted))),
          TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: Text(l10n.actionAccept,
                  style: AppType.label(c, color: c.green)
                      .copyWith(fontWeight: FontWeight.w700))),
        ],
      ),
    );
  }
}

class _OwnerApplicationCard extends StatelessWidget {
  const _OwnerApplicationCard(
      {required this.app, required this.locked, required this.onDecide});
  final RentalApplication app;
  final bool locked;
  final ValueChanged<String> onDecide;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: c.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundColor: c.greenSoft,
                child: Text(
                  (app.renterName ?? '?').characters.first.toUpperCase(),
                  style: AppType.headline(c).copyWith(color: c.green),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(app.renterName ?? l10n.defaultApplicantLabel,
                        style: AppType.headline(c).copyWith(fontSize: 16)),
                    if (app.renterPhone != null)
                      Text(app.renterPhone!,
                          style: AppType.mono(c, size: 12, color: c.inkMuted)),
                  ],
                ),
              ),
              StatusPill(app.status),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Text('${l10n.labelOffer}  ',
                  style: AppType.label(c, color: c.inkMuted)),
              Flexible(
                child: Text('${Fmt.rent(app.offeredRent)}${l10n.perMonthSuffixShort}',
                    overflow: TextOverflow.ellipsis,
                    style:
                        AppType.mono(c, size: 16, weight: FontWeight.w700)),
              ),
            ],
          ),
          if (app.message != null && app.message!.isNotEmpty) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(11),
              decoration: BoxDecoration(
                  color: c.surfaceSunken.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(10)),
              child: Text(app.message!,
                  style: AppType.label(c, color: c.inkSecondary)),
            ),
          ],
          if (app.isPending && !locked) ...[
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: GhostButton(
                    label: l10n.actionDecline,
                    danger: true,
                    onPressed: () => onDecide('reject'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: PrimaryButton(
                    label: l10n.actionAccept,
                    onPressed: () => onDecide('accept'),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
