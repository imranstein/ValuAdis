import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/auth/auth_bloc.dart';
import '../../../blocs/cubits.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/owner_listing.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../widgets/band_range_bar.dart';
import '../../widgets/buttons.dart';
import '../../widgets/pills.dart';
import '../../widgets/pressable.dart';
import '../../widgets/screen_header.dart';
import '../../widgets/states.dart';
import 'listing_applications_screen.dart';
import 'photo_manager_screen.dart';
import 'property_register_screen.dart';

class OwnerListingsScreen extends StatelessWidget {
  const OwnerListingsScreen({super.key});

  Future<void> _register(BuildContext context) async {
    final repo = context.read<RentalsRepository>();
    final cubit = context.read<MyListingsCubit>();
    final created = await Navigator.of(context).push<bool>(MaterialPageRoute(
      builder: (_) => PropertyRegisterScreen(repo: repo),
    ));
    if (created == true) cubit.load();
  }

  void _openApplications(BuildContext context, OwnerListing listing) {
    final repo = context.read<RentalsRepository>();
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => BlocProvider(
        create: (_) =>
            ListingApplicationsCubit(repo, listing.publicId)..load(),
        child: ListingApplicationsScreen(listing: listing),
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final cubit = context.read<MyListingsCubit>();
    final user = context.watch<AuthBloc>().state.user;
    final needsVerification = user?.needsOwnerVerification ?? false;

    return SafeArea(
      bottom: false,
      child: Column(
        children: [
          ScreenHeader(
            title: 'My listings',
            subtitle: 'Properties you have put up for rent',
            trailing: HeaderIconButton(
                icon: Icons.add, onTap: () => _register(context)),
          ),
          if (needsVerification) const _VerificationBanner(),
          Expanded(
            child: BlocBuilder<MyListingsCubit,
                AsyncState<List<OwnerListing>>>(
              builder: (context, state) {
                if (state.isError) {
                  return ErrorView(
                      message: state.error ?? 'Could not load listings.',
                      onRetry: cubit.load);
                }
                if (!state.isReady) {
                  return const Center(child: CircularProgressIndicator());
                }
                final listings = state.data!;
                if (listings.isEmpty) {
                  return EmptyState(
                    icon: Icons.home_work_outlined,
                    title: 'List your first property',
                    message:
                        'Register a property and we will suggest an honest rent '
                        'band from an official valuation. An officer reviews it '
                        'before it goes public.',
                    actionLabel: 'Register a property',
                    onAction: () => _register(context),
                  );
                }
                return RefreshIndicator(
                  color: c.green,
                  onRefresh: cubit.refresh,
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: listings.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 14),
                    itemBuilder: (context, i) => StaggeredReveal(
                      index: i,
                      child: _OwnerListingCard(
                        listing: listings[i],
                        onTap: () => _openApplications(context, listings[i]),
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

class _VerificationBanner extends StatelessWidget {
  const _VerificationBanner();

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 4, 16, 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: c.goldWash,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: c.gold.withValues(alpha: 0.35)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.hourglass_top_outlined, size: 20, color: c.gold),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Verification pending',
                    style: AppType.label(c, color: c.ink)
                        .copyWith(fontWeight: FontWeight.w700)),
                const SizedBox(height: 3),
                Text(
                  'A rental officer is reviewing your Fayda ID. You can prepare '
                  'listings now, but they publish only after you are verified.',
                  style: AppType.caption(c, color: c.inkSecondary)
                      .copyWith(height: 1.45),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _OwnerListingCard extends StatefulWidget {
  const _OwnerListingCard({required this.listing, required this.onTap});
  final OwnerListing listing;
  final VoidCallback onTap;

  @override
  State<_OwnerListingCard> createState() => _OwnerListingCardState();
}

class _OwnerListingCardState extends State<_OwnerListingCard> {
  bool _downloadingAgreement = false;

  void _openPhotos(BuildContext context) {
    final listing = widget.listing;
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => PhotoManagerScreen(
        propertyId: listing.propertyId,
        propertyAddress: listing.propertyAddress ?? listing.publicId,
      ),
    ));
  }

  Future<void> _downloadAgreement() async {
    setState(() => _downloadingAgreement = true);
    final repo = context.read<RentalsRepository>();
    try {
      final bytes = await repo
          .downloadListingAgreementPdf(widget.listing.publicId);
      final dir = await getTemporaryDirectory();
      final file = File(
          '${dir.path}/ValuAdis_Agreement_${widget.listing.publicId}.pdf');
      await file.writeAsBytes(bytes);
      await OpenFilex.open(file.path);
    } on RentalsException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(SnackBar(content: Text(e.message)));
      }
    } finally {
      if (mounted) setState(() => _downloadingAgreement = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final listing = widget.listing;
    final showAgreement = listing.isPublished && listing.hasAgreement;
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
          Pressable(
            onTap: widget.onTap,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(listing.propertyAddress ?? listing.publicId,
                          style: AppType.headline(c).copyWith(fontSize: 16)),
                    ),
                    const SizedBox(width: 10),
                    StatusPill(listing.status),
                  ],
                ),
                const SizedBox(height: 6),
                Text(listing.publicId,
                    style: AppType.mono(c, size: 12, color: c.inkMuted)),
                const SizedBox(height: 14),
                BandRangeBar(band: listing.band),
                if (listing.reviewReason != null &&
                    listing.reviewReason!.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                        color: c.surfaceSunken.withValues(alpha: 0.5),
                        borderRadius: BorderRadius.circular(10)),
                    child: Text('Officer note: ${listing.reviewReason}',
                        style: AppType.caption(c, color: c.inkSecondary)),
                  ),
                ],
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Flexible(
                      child: Text(
                          listing.isPublished
                              ? 'Published ${Fmt.date(listing.publishedAt)}'
                              : 'Created ${Fmt.date(listing.createdAt)}',
                          overflow: TextOverflow.ellipsis,
                          style: AppType.caption(c, color: c.inkMuted)),
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('View applications',
                            style: AppType.caption(c, color: c.green)
                                .copyWith(fontWeight: FontWeight.w600)),
                        Icon(Icons.chevron_right, size: 16, color: c.green),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Divider(height: 1, color: c.border),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: GhostButton(
                  label: 'Manage photos',
                  icon: Icons.photo_camera_outlined,
                  expand: true,
                  onPressed: () => _openPhotos(context),
                ),
              ),
              if (showAgreement) ...[
                const SizedBox(width: 10),
                Expanded(
                  child: GhostButton(
                    label: _downloadingAgreement ? 'Preparing...' : 'Agreement',
                    icon: Icons.picture_as_pdf_outlined,
                    expand: true,
                    onPressed: _downloadingAgreement
                        ? null
                        : _downloadAgreement,
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
