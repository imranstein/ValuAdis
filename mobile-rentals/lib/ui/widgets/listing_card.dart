import 'package:flutter/material.dart';

import '../../core/formatting.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/listing.dart';
import '../../l10n/app_localizations.dart';
import 'band_range_bar.dart';
import 'listing_placeholder.dart';
import 'network_photo.dart';
import 'pills.dart';
import 'pressable.dart';

/// The hero browse surface: photography-forward image zone (a real cached photo
/// when the listing has one, else the branded placeholder), price overlay in
/// mono, the certified trust mark, then address, sub-city, a compact facts row,
/// and the visual band range.
class ListingCard extends StatelessWidget {
  const ListingCard({super.key, required this.listing, this.onTap});

  final Listing listing;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context);
    final p = listing.property;

    return Pressable(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: c.border),
          boxShadow: [
            BoxShadow(
              color: c.ink.withValues(alpha: c.isDark ? 0.28 : 0.05),
              blurRadius: 24,
              offset: const Offset(0, 12),
            ),
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AspectRatio(
              aspectRatio: 16 / 10,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Hero(
                    tag: 'listing-image-${listing.publicId}',
                    child: p.hasPhotos
                        ? NetworkPhoto(
                            url: p.photoUrls.first,
                            errorPlaceholder: ListingPlaceholder(
                              seed: listing.publicId,
                              propertySubtype: p.propertySubtype,
                            ),
                          )
                        : ListingPlaceholder(
                            seed: listing.publicId,
                            propertySubtype: p.propertySubtype,
                          ),
                  ),
                  if (listing.hasCertificate)
                    const Positioned(
                        top: 12, right: 12, child: CertifiedBadge(onDark: true)),
                  Positioned(
                    left: 14,
                    bottom: 12,
                    child: _PriceTag(listing: listing),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    p.address,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppType.headline(c),
                  ),
                  const SizedBox(height: 3),
                  Row(
                    children: [
                      Icon(Icons.location_on_outlined,
                          size: 14, color: c.inkMuted),
                      const SizedBox(width: 3),
                      Text(
                        [p.subcity, p.municipality]
                            .where((e) => e != null && e.isNotEmpty)
                            .join(', '),
                        style: AppType.label(c, color: c.inkMuted),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 16,
                    runSpacing: 6,
                    children: [
                      if (p.bedrooms != null)
                        MetaChip(
                            icon: Icons.bed_outlined,
                            label: l10n?.bedCount(p.bedrooms!) ??
                                '${p.bedrooms} bed'),
                      if (p.bathrooms != null)
                        MetaChip(
                            icon: Icons.bathtub_outlined,
                            label: l10n?.bathCount(p.bathrooms!) ??
                                '${p.bathrooms} bath'),
                      MetaChip(
                          icon: Icons.straighten_outlined,
                          label: '${p.areaSqm.round()} m2'),
                      if (p.propertySubtype != null)
                        MetaChip(
                            icon: Icons.home_work_outlined,
                            label: Fmt.humanize(p.propertySubtype)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  BandRangeBar(band: listing.band, showLabels: true),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PriceTag extends StatelessWidget {
  const _PriceTag({required this.listing});
  final Listing listing;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Hero(
      tag: 'listing-price-${listing.publicId}',
      child: Material(
        color: Colors.transparent,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
          decoration: BoxDecoration(
            color: Colors.black.withValues(alpha: 0.42),
            borderRadius: BorderRadius.circular(12),
          ),
          // ClipRect absorbs the sub-pixel RenderFlex overflow that mixed
          // Latin/Ethiopic font metrics can trigger on a baseline-aligned
          // Row (a known Flutter float-precision quirk, not real clipped
          // content — the suffix text itself is short and never truncated).
          child: ClipRect(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(Fmt.rent(listing.band.suggested),
                    style: AppType.mono(c,
                        size: 17, weight: FontWeight.w700, color: c.onGreen)),
                const SizedBox(width: 4),
                Text(AppLocalizations.of(context)?.perMonthSuffixShort ?? '/mo',
                    style: AppType.caption(c,
                        color: c.onGreen.withValues(alpha: 0.8))),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
