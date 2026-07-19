import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/cubits.dart';
import '../../../core/constants.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/listing.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/buttons.dart';
import '../../widgets/inputs.dart';
import '../../widgets/listing_card.dart';
import '../../widgets/pressable.dart';
import '../../widgets/screen_header.dart';
import '../../widgets/states.dart';
import '../shared/activity_screen.dart';
import 'listing_detail_screen.dart';

class BrowseScreen extends StatefulWidget {
  const BrowseScreen({super.key});

  @override
  State<BrowseScreen> createState() => _BrowseScreenState();
}

class _BrowseScreenState extends State<BrowseScreen> {
  bool _mapMode = false;

  void _openListing(String publicId) {
    final repo = context.read<RentalsRepository>();
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => BlocProvider(
        create: (_) => ListingDetailCubit(repo, publicId)..load(),
        child: ListingDetailScreen(publicId: publicId),
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final cubit = context.watch<BrowseCubit>();
    return SafeArea(
      bottom: false,
      child: Column(
        children: [
          ScreenHeader(
            title: l10n.screenTitleFindHome,
            subtitle: l10n.screenSubtitleFindHome,
            trailing: HeaderIconButton(
              icon: Icons.notifications_none,
              onTap: () => Navigator.of(context).push(MaterialPageRoute(
                  builder: (_) => const ActivityScreen())),
            ),
          ),
          _Toolbar(
            cubit: cubit,
            mapMode: _mapMode,
            onToggleMode: (v) => setState(() => _mapMode = v),
          ),
          Expanded(
            child: BlocBuilder<BrowseCubit, AsyncState<List<Listing>>>(
              builder: (context, state) {
                if (state.isLoading || state.status == LoadStatus.initial) {
                  return ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: 3,
                    separatorBuilder: (_, _) => const SizedBox(height: 16),
                    itemBuilder: (_, _) => const ListingCardSkeleton(),
                  );
                }
                if (state.isError) {
                  return ErrorView(
                      message: state.error ?? l10n.errorLoadListings,
                      onRetry: cubit.load);
                }
                final listings = state.data ?? const <Listing>[];
                if (listings.isEmpty) {
                  return EmptyState(
                    icon: Icons.travel_explore_outlined,
                    title: l10n.emptyNoMatchesTitle,
                    message: cubit.hasFilters
                        ? l10n.emptyNoMatchesFilteredMessage
                        : l10n.emptyNoMatchesMessage,
                    actionLabel: cubit.hasFilters ? l10n.actionClearFilters : null,
                    onAction: cubit.hasFilters ? cubit.clearFilters : null,
                  );
                }
                return _mapMode
                    ? _MapResults(listings: listings, onTap: _openListing)
                    : RefreshIndicator(
                        color: c.green,
                        onRefresh: cubit.refresh,
                        child: ListView.separated(
                          padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                          itemCount: listings.length,
                          separatorBuilder: (_, _) =>
                              const SizedBox(height: 16),
                          itemBuilder: (context, i) => StaggeredReveal(
                            index: i,
                            child: ListingCard(
                              listing: listings[i],
                              onTap: () => _openListing(listings[i].publicId),
                            ),
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

class _Toolbar extends StatelessWidget {
  const _Toolbar(
      {required this.cubit,
      required this.mapMode,
      required this.onToggleMode});
  final BrowseCubit cubit;
  final bool mapMode;
  final ValueChanged<bool> onToggleMode;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final filterLabel = cubit.hasFilters
        ? [
            cubit.subCity,
            if (cubit.bedrooms != null) l10n.bedCount(cubit.bedrooms!),
            if (cubit.maxRent != null)
              l10n.maxRentSummary(Fmt.rent(cubit.maxRent!)),
          ].where((e) => e != null).join(' · ')
        : l10n.filterListingsLabel;
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
      child: Row(
        children: [
          Expanded(
            child: Pressable(
              onTap: () => _openFilterSheet(context, cubit),
              child: Container(
                height: 46,
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                  color: c.surface,
                  borderRadius: BorderRadius.circular(13),
                  border: Border.all(
                      color: cubit.hasFilters ? c.green : c.border,
                      width: cubit.hasFilters ? 1.5 : 1),
                ),
                child: Row(
                  children: [
                    Icon(Icons.tune,
                        size: 18,
                        color: cubit.hasFilters ? c.green : c.inkMuted),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(filterLabel,
                          overflow: TextOverflow.ellipsis,
                          style: AppType.label(c,
                              color: cubit.hasFilters ? c.ink : c.inkMuted,
                              weight: cubit.hasFilters
                                  ? FontWeight.w600
                                  : FontWeight.w500)),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          _ModeToggle(mapMode: mapMode, onToggle: onToggleMode),
        ],
      ),
    );
  }
}

class _ModeToggle extends StatelessWidget {
  const _ModeToggle({required this.mapMode, required this.onToggle});
  final bool mapMode;
  final ValueChanged<bool> onToggle;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    Widget seg(IconData icon, bool active, VoidCallback onTap) => Pressable(
          onTap: onTap,
          scale: 0.9,
          child: Container(
            width: 42,
            height: 46,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: active ? c.green : Colors.transparent,
              borderRadius: BorderRadius.circular(11),
            ),
            child: Icon(icon,
                size: 19, color: active ? c.onGreen : c.inkMuted),
          ),
        );
    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(13),
        border: Border.all(color: c.border),
      ),
      child: Row(
        children: [
          seg(Icons.view_agenda_outlined, !mapMode, () => onToggle(false)),
          seg(Icons.map_outlined, mapMode, () => onToggle(true)),
        ],
      ),
    );
  }
}

class _MapResults extends StatelessWidget {
  const _MapResults({required this.listings, required this.onTap});
  final List<Listing> listings;
  final void Function(String publicId) onTap;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final located =
        listings.where((l) => l.property.hasLocation).toList();
    return Stack(
      children: [
        FlutterMap(
          options: const MapOptions(
            initialCenter:
                LatLng(AppConstants.defaultLat, AppConstants.defaultLon),
            initialZoom: AppConstants.defaultZoom,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.valuadis.rent',
            ),
            MarkerLayer(
              markers: [
                for (final l in located)
                  Marker(
                    point: LatLng(
                        l.property.latitude!, l.property.longitude!),
                    width: 96,
                    height: 40,
                    child: Pressable(
                      onTap: () => onTap(l.publicId),
                      child: _MapPill(text: Fmt.rent(l.band.suggested)),
                    ),
                  ),
              ],
            ),
          ],
        ),
        if (located.length < listings.length)
          Positioned(
            left: 16,
            right: 16,
            bottom: 16,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: c.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: c.border),
              ),
              child: Text(
                AppLocalizations.of(context)!.mapPinMissingInfo(
                    listings.length - located.length, listings.length),
                style: AppType.caption(c, color: c.inkSecondary),
              ),
            ),
          ),
      ],
    );
  }
}

class _MapPill extends StatelessWidget {
  const _MapPill({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: c.green,
        borderRadius: BorderRadius.circular(999),
        boxShadow: [
          BoxShadow(
              color: c.ink.withValues(alpha: 0.2),
              blurRadius: 8,
              offset: const Offset(0, 3)),
        ],
      ),
      child: Text(text,
          style: AppType.mono(c,
              size: 12, weight: FontWeight.w700, color: c.onGreen)),
    );
  }
}

Future<void> _openFilterSheet(BuildContext context, BrowseCubit cubit) async {
  final c = AppColors.of(context);
  final l10n = AppLocalizations.of(context)!;
  String? subCity = cubit.subCity;
  int? bedrooms = cubit.bedrooms;
  final maxRentCtrl = TextEditingController(
      text: cubit.maxRent == null ? '' : cubit.maxRent!.round().toString());

  await showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: c.surface,
    builder: (sheetContext) {
      return StatefulBuilder(
        builder: (context, setSheet) {
          return Padding(
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 18,
              bottom: MediaQuery.of(context).viewInsets.bottom + 24,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                        color: c.border,
                        borderRadius: BorderRadius.circular(999)),
                  ),
                ),
                const SizedBox(height: 18),
                Text(l10n.filterSheetTitle, style: AppType.title(c)),
                const SizedBox(height: 18),
                AppDropdownField<String?>(
                  label: l10n.fieldSubCity,
                  value: subCity,
                  hint: l10n.hintAnySubCity,
                  items: <String?>[null, ...AppConstants.addisSubCities],
                  itemLabel: (v) => v ?? l10n.hintAnySubCity,
                  onChanged: (v) => setSheet(() => subCity = v),
                ),
                const SizedBox(height: 14),
                Text(l10n.fieldBedrooms,
                    style: AppType.label(c, color: c.inkSecondary)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: [
                    for (final n in <int?>[null, 1, 2, 3, 4])
                      _ChoiceChipX(
                        label: n == null ? l10n.labelAny : l10n.bedCountPlus(n),
                        selected: bedrooms == n,
                        onTap: () => setSheet(() => bedrooms = n),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                AppTextField(
                  label: l10n.fieldMaxRent,
                  controller: maxRentCtrl,
                  keyboardType: TextInputType.number,
                  hint: l10n.hintNoLimit,
                  prefixIcon: Icons.payments_outlined,
                ),
                const SizedBox(height: 22),
                PrimaryButton(
                  label: l10n.actionShowResults,
                  onPressed: () {
                    final maxRent = double.tryParse(maxRentCtrl.text.trim());
                    cubit.applyFilters(
                        subCity: subCity,
                        bedrooms: bedrooms,
                        maxRent: maxRent);
                    Navigator.of(context).pop();
                  },
                ),
                const SizedBox(height: 8),
                Center(
                  child: TextButton(
                    onPressed: () {
                      cubit.clearFilters();
                      Navigator.of(context).pop();
                    },
                    child: Text(l10n.actionResetFilters,
                        style: AppType.label(c, color: c.inkMuted)),
                  ),
                ),
              ],
            ),
          );
        },
      );
    },
  );
  maxRentCtrl.dispose();
}

class _ChoiceChipX extends StatelessWidget {
  const _ChoiceChipX(
      {required this.label, required this.selected, required this.onTap});
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Pressable(
      onTap: onTap,
      scale: 0.94,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 9),
        decoration: BoxDecoration(
          color: selected ? c.green : c.surfaceSunken.withValues(alpha: 0.6),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: selected ? c.green : c.border),
        ),
        child: Text(label,
            style: AppType.label(c,
                color: selected ? c.onGreen : c.inkSecondary,
                weight: FontWeight.w600)),
      ),
    );
  }
}
