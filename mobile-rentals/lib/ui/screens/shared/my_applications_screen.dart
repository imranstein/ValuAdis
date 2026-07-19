import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/cubits.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/application.dart';
import '../../../data/models/band.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/band_range_bar.dart';
import '../../widgets/pills.dart';
import '../../widgets/screen_header.dart';
import '../../widgets/states.dart';

class MyApplicationsScreen extends StatelessWidget {
  const MyApplicationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final cubit = context.read<MyApplicationsCubit>();
    return SafeArea(
      bottom: false,
      child: Column(
        children: [
          ScreenHeader(
              title: l10n.screenTitleMyApplications,
              subtitle: l10n.screenSubtitleMyApplications),
          Expanded(
            child: BlocBuilder<MyApplicationsCubit,
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
                    icon: Icons.assignment_outlined,
                    title: l10n.emptyNoApplicationsTitle,
                    message: l10n.renterEmptyApplicationsMessage,
                  );
                }
                return RefreshIndicator(
                  color: c.green,
                  onRefresh: cubit.refresh,
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: apps.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 14),
                    itemBuilder: (context, i) => StaggeredReveal(
                      index: i,
                      child: _ApplicationCard(app: apps[i]),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _ApplicationCard extends StatelessWidget {
  const _ApplicationCard({required this.app});
  final RentalApplication app;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final hasBand = app.bandMin != null && app.bandMax != null;
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                    app.propertyAddress ??
                        l10n.defaultListingLabel(app.listingPublicId ?? ''),
                    style: AppType.headline(c).copyWith(fontSize: 16)),
              ),
              const SizedBox(width: 10),
              StatusPill(app.status),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Text('${l10n.labelYourOffer}  ',
                  style: AppType.label(c, color: c.inkMuted)),
              Flexible(
                child: Text('${Fmt.rent(app.offeredRent)}${l10n.perMonthSuffixShort}',
                    overflow: TextOverflow.ellipsis,
                    style: AppType.mono(c, size: 15, weight: FontWeight.w700)),
              ),
            ],
          ),
          if (hasBand) ...[
            const SizedBox(height: 14),
            BandRangeBar(
              band: RentBand(
                  min: app.bandMin!,
                  max: app.bandMax!,
                  suggested: (app.bandMin! + app.bandMax!) / 2),
              offer: app.offeredRent,
              showLabels: false,
            ),
          ],
          const SizedBox(height: 12),
          Text(l10n.appliedOnLabel(Fmt.date(app.createdAt)),
              style: AppType.caption(c, color: c.inkMuted)),
        ],
      ),
    );
  }
}
