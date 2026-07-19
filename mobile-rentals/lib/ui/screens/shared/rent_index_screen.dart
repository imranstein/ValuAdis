import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/cubits.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/rent_index.dart';
import '../../widgets/brand.dart';
import '../../widgets/screen_header.dart';
import '../../widgets/states.dart';

class RentIndexScreen extends StatelessWidget {
  const RentIndexScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<RentIndexCubit>();
    return SafeArea(
      bottom: false,
      child: Column(
        children: [
          const ScreenHeader(
              title: 'Rent index',
              subtitle: 'Median registered rents by sub-city'),
          Expanded(
            child: BlocBuilder<RentIndexCubit,
                AsyncState<List<RentIndexRow>>>(
              builder: (context, state) {
                if (state.isError) {
                  return ErrorView(
                      message: state.error ?? 'Could not load the index.',
                      onRetry: cubit.load);
                }
                if (!state.isReady) {
                  return const Center(child: CircularProgressIndicator());
                }
                final rows = state.data!;
                if (rows.isEmpty) {
                  return const EmptyState(
                    icon: Icons.insights_outlined,
                    title: 'Index still building',
                    message:
                        'The index publishes a median only where enough contracts '
                        'have been registered. As the registry grows, medians per '
                        'sub-city appear here.',
                  );
                }
                final byDistrict = <String, List<RentIndexRow>>{};
                for (final r in rows) {
                  byDistrict.putIfAbsent(r.district, () => []).add(r);
                }
                final districts = byDistrict.keys.toList()..sort();
                return ListView(
                  padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
                  children: [
                    _IndexIntro(period: rows.first.period),
                    const SizedBox(height: 16),
                    for (var i = 0; i < districts.length; i++)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 14),
                        child: StaggeredReveal(
                          index: i,
                          child: _DistrictCard(
                              district: districts[i],
                              rows: byDistrict[districts[i]]!),
                        ),
                      ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _IndexIntro extends StatelessWidget {
  const _IndexIntro({required this.period});
  final String period;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: c.greenSoft.withValues(alpha: c.isDark ? 0.45 : 0.4),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          const RegistrySeal(size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Medians from registered tenancy contracts for $period. Low-sample '
              'cells are hidden, so what you see is real.',
              style: AppType.label(c, color: c.inkSecondary).copyWith(height: 1.4),
            ),
          ),
        ],
      ),
    );
  }
}

class _DistrictCard extends StatelessWidget {
  const _DistrictCard({required this.district, required this.rows});
  final String district;
  final List<RentIndexRow> rows;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final sorted = [...rows]
      ..sort((a, b) => (a.bedrooms ?? 0).compareTo(b.bedrooms ?? 0));
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
              Icon(Icons.location_city_outlined, size: 18, color: c.green),
              const SizedBox(width: 8),
              Text(district, style: AppType.headline(c)),
            ],
          ),
          const SizedBox(height: 6),
          for (final r in sorted) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Text(
                    [
                      Fmt.humanize(r.propertySubtype),
                      if (r.bedrooms != null) '${r.bedrooms} bed',
                    ].where((e) => e.isNotEmpty).join(' · '),
                    style: AppType.label(c, color: c.inkSecondary),
                  ),
                ),
                Text('n=${r.sampleSize}',
                    style: AppType.caption(c, color: c.inkMuted)),
                const SizedBox(width: 12),
                Text(Fmt.rentPerMonth(r.medianRent),
                    style: AppType.mono(c, size: 15, weight: FontWeight.w700)),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
