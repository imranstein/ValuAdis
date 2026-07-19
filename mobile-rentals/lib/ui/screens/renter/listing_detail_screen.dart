import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/cubits.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/listing.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/band_range_bar.dart';
import '../../widgets/buttons.dart';
import '../../widgets/listing_placeholder.dart';
import '../../widgets/map_preview.dart';
import '../../widgets/photo_carousel.dart';
import '../../widgets/pills.dart';
import '../../widgets/states.dart';
import 'apply_sheet.dart';

class ListingDetailScreen extends StatelessWidget {
  const ListingDetailScreen({super.key, required this.publicId});
  final String publicId;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      body: BlocBuilder<ListingDetailCubit, AsyncState<Listing>>(
        builder: (context, state) {
          if (state.isError) {
            return SafeArea(
              child: Column(
                children: [
                  _BackBar(publicId: publicId),
                  Expanded(
                    child: ErrorView(
                        message: state.error ??
                            AppLocalizations.of(context)!.errorLoadListing,
                        onRetry: context.read<ListingDetailCubit>().load),
                  ),
                ],
              ),
            );
          }
          if (!state.isReady || state.data == null) {
            return SafeArea(
              child: Column(
                children: [
                  _BackBar(publicId: publicId),
                  const Expanded(
                      child: Center(child: CircularProgressIndicator())),
                ],
              ),
            );
          }
          return _DetailBody(listing: state.data!);
        },
      ),
    );
  }
}

class _DetailBody extends StatelessWidget {
  const _DetailBody({required this.listing});
  final Listing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final p = listing.property;
    return Stack(
      children: [
        CustomScrollView(
          slivers: [
            SliverAppBar(
              expandedHeight: 280,
              pinned: true,
              backgroundColor: c.canvas,
              leading: _CircleBack(),
              flexibleSpace: FlexibleSpaceBar(
                background: Stack(
                  fit: StackFit.expand,
                  children: [
                    Hero(
                      tag: 'listing-image-${listing.publicId}',
                      child: PhotoCarousel(
                        urls: p.photoUrls,
                        placeholder: ListingPlaceholder(
                            seed: listing.publicId,
                            propertySubtype: p.propertySubtype,
                            showNote: false),
                      ),
                    ),
                    if (listing.hasCertificate)
                      const Positioned(
                          top: 60, right: 16, child: CertifiedBadge(onDark: true)),
                  ],
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 140),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Hero(
                          tag: 'listing-price-${listing.publicId}',
                          child: Material(
                            color: Colors.transparent,
                            child: Text(Fmt.rent(listing.band.suggested),
                                style: AppType.mono(c,
                                    size: 28, weight: FontWeight.w700)),
                          ),
                        ),
                        const SizedBox(width: 4),
                        Padding(
                          padding: const EdgeInsets.only(bottom: 5),
                          child: Text(l10n.perMonthSuffix,
                              style: AppType.label(c, color: c.inkMuted)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(p.address, style: AppType.title(c)),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.location_on_outlined,
                            size: 15, color: c.inkMuted),
                        const SizedBox(width: 4),
                        Flexible(
                          child: Text(
                              [p.subcity, p.municipality]
                                  .where((e) => e != null && e.isNotEmpty)
                                  .join(', '),
                              overflow: TextOverflow.ellipsis,
                              style: AppType.label(c, color: c.inkMuted)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    _FactsRow(listing: listing),
                    const SizedBox(height: 22),
                    _BandPanel(listing: listing),
                    const SizedBox(height: 22),
                    Text(l10n.sectionLocation, style: AppType.headline(c)),
                    const SizedBox(height: 12),
                    MapPreview(
                        latitude: p.latitude, longitude: p.longitude),
                    const SizedBox(height: 22),
                    _PropertyDetails(listing: listing),
                  ],
                ),
              ),
            ),
          ],
        ),
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: _ApplyBar(listing: listing),
        ),
      ],
    );
  }
}

class _FactsRow extends StatelessWidget {
  const _FactsRow({required this.listing});
  final Listing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final p = listing.property;
    final facts = <(IconData, String, String)>[
      if (p.bedrooms != null)
        (Icons.bed_outlined, '${p.bedrooms}', l10n.fieldBedrooms),
      if (p.bathrooms != null)
        (Icons.bathtub_outlined, '${p.bathrooms}', l10n.fieldBathrooms),
      (Icons.straighten_outlined, '${p.areaSqm.round()}', l10n.labelAreaM2),
    ];
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: c.border),
      ),
      child: Row(
        children: [
          for (var i = 0; i < facts.length; i++) ...[
            Expanded(
              child: Column(
                children: [
                  Icon(facts[i].$1, size: 20, color: c.green),
                  const SizedBox(height: 6),
                  Text(facts[i].$2,
                      style: AppType.mono(c, size: 16, weight: FontWeight.w700)),
                  Text(facts[i].$3,
                      style: AppType.caption(c, color: c.inkMuted)),
                ],
              ),
            ),
            if (i < facts.length - 1)
              Container(width: 1, height: 34, color: c.border),
          ],
        ],
      ),
    );
  }
}

class _BandPanel extends StatelessWidget {
  const _BandPanel({required this.listing});
  final Listing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: c.greenSoft.withValues(alpha: c.isDark ? 0.5 : 0.45),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: c.green.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.balance_outlined, size: 18, color: c.green),
              const SizedBox(width: 8),
              Flexible(
                child: Text(l10n.bandPanelTitle,
                    style: AppType.headline(c).copyWith(fontSize: 16)),
              ),
            ],
          ),
          const SizedBox(height: 16),
          BandRangeBar(band: listing.band),
          const SizedBox(height: 14),
          Text(
            l10n.bandPanelBody,
            style: AppType.label(c, color: c.inkSecondary).copyWith(height: 1.45),
          ),
        ],
      ),
    );
  }
}

class _PropertyDetails extends StatelessWidget {
  const _PropertyDetails({required this.listing});
  final Listing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    final p = listing.property;
    final rows = <(String, String?)>[
      (l10n.labelPropertyType, Fmt.humanize(p.propertyType)),
      (l10n.fieldSubtype,
          p.propertySubtype == null ? null : Fmt.humanize(p.propertySubtype)),
      (l10n.fieldCondition,
          p.condition == null ? null : Fmt.humanize(p.condition)),
      (l10n.fieldYearBuilt, p.yearBuilt?.toString()),
      (l10n.labelFloors, p.floors?.toString()),
      (l10n.labelPublished, Fmt.date(listing.publishedAt)),
    ].where((r) => r.$2 != null && r.$2!.isNotEmpty).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(l10n.propertyDetailsTitle, style: AppType.headline(c)),
        const SizedBox(height: 8),
        for (final r in rows)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 9),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(r.$1, style: AppType.label(c, color: c.inkMuted)),
                Flexible(
                  child: Text(r.$2!,
                      textAlign: TextAlign.right,
                      overflow: TextOverflow.ellipsis,
                      style: AppType.label(c,
                          color: c.ink, weight: FontWeight.w600)),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _ApplyBar extends StatelessWidget {
  const _ApplyBar({required this.listing});
  final Listing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
      decoration: BoxDecoration(
        color: c.surface,
        border: Border(top: BorderSide(color: c.border)),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                      l10n.bandRangeLabel(Fmt.rent(listing.band.min),
                          Fmt.rent(listing.band.max)),
                      overflow: TextOverflow.ellipsis,
                      style: AppType.mono(c, size: 12, color: c.inkMuted)),
                  Text(l10n.chooseYourOfferLabel,
                      overflow: TextOverflow.ellipsis,
                      style: AppType.label(c, color: c.inkSecondary)),
                ],
              ),
            ),
            const SizedBox(width: 12),
            PrimaryButton(
              label: l10n.actionApply,
              icon: Icons.send_outlined,
              expand: false,
              onPressed: () => showApplySheet(context, listing),
            ),
          ],
        ),
      ),
    );
  }
}

class _CircleBack extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Material(
        color: c.surface.withValues(alpha: 0.9),
        shape: const CircleBorder(),
        child: InkWell(
          customBorder: const CircleBorder(),
          onTap: () => Navigator.of(context).maybePop(),
          child: Icon(Icons.arrow_back, size: 20, color: c.ink),
        ),
      ),
    );
  }
}

class _BackBar extends StatelessWidget {
  const _BackBar({required this.publicId});
  final String publicId;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: BackButton(onPressed: () => Navigator.of(context).maybePop()),
      ),
    );
  }
}
