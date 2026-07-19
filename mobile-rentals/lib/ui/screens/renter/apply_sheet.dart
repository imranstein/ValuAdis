import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/listing.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../widgets/band_range_bar.dart';
import '../../widgets/buttons.dart';
import '../../widgets/inputs.dart';

/// Opens the apply sheet. The offer slider is clamped to the listing's band, so
/// the renter can never propose an amount the server would reject; the band is
/// re-validated server-side regardless.
Future<void> showApplySheet(BuildContext context, Listing listing) {
  final repo = context.read<RentalsRepository>();
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => _ApplySheet(listing: listing, repo: repo),
  );
}

class _ApplySheet extends StatefulWidget {
  const _ApplySheet({required this.listing, required this.repo});
  final Listing listing;
  final RentalsRepository repo;

  @override
  State<_ApplySheet> createState() => _ApplySheetState();
}

class _ApplySheetState extends State<_ApplySheet> {
  late double _offer = widget.listing.band.suggested;
  final _message = TextEditingController();
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    _message.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await widget.repo.apply(
        widget.listing.publicId,
        double.parse(_offer.roundToDouble().toStringAsFixed(0)),
        _message.text.trim().isEmpty ? null : _message.text.trim(),
      );
      if (!mounted) return;
      Navigator.of(context).pop(); // close sheet
      Navigator.of(context).pop(); // close detail, back to browse
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(
            content: Text(
                'Application sent at ${Fmt.rent(_offer)}. Track it under Applications.')));
    } on RentalsException catch (e) {
      setState(() {
        _error = e.message;
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final band = widget.listing.band;
    // ~25 ETB per step keeps the thumb precise on narrow bands and still
    // manageable on wide ones.
    final divisions = ((band.max - band.min) / 25).round().clamp(10, 400);
    return Container(
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 14,
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
                  color: c.border, borderRadius: BorderRadius.circular(999)),
            ),
          ),
          const SizedBox(height: 18),
          Text('Apply to rent', style: AppType.title(c)),
          const SizedBox(height: 2),
          Text(widget.listing.property.address,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: AppType.label(c, color: c.inkMuted)),
          const SizedBox(height: 22),
          Center(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 150),
              transitionBuilder: (child, anim) =>
                  FadeTransition(opacity: anim, child: child),
              child: Text(
                Fmt.rentPerMonth(_offer),
                key: ValueKey(_offer.round()),
                style: AppType.mono(c, size: 30, weight: FontWeight.w700),
              ),
            ),
          ),
          const SizedBox(height: 6),
          Center(
            child: Text('Within the allowed band',
                style: AppType.caption(c, color: c.green)
                    .copyWith(fontWeight: FontWeight.w600)),
          ),
          const SizedBox(height: 14),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: c.green,
              inactiveTrackColor: c.surfaceSunken,
              thumbColor: c.green,
              overlayColor: c.green.withValues(alpha: 0.12),
              trackHeight: 5,
            ),
            child: Slider(
              min: band.min,
              max: band.max,
              divisions: divisions,
              value: band.clamp(_offer),
              onChanged: _submitting
                  ? null
                  : (v) => setState(() => _offer = v),
            ),
          ),
          BandRangeBar(band: band, offer: _offer, showLabels: true),
          const SizedBox(height: 18),
          AppTextField(
            label: 'Message to the owner (optional)',
            controller: _message,
            hint: 'Introduce yourself, move-in date, etc.',
            maxLines: 3,
          ),
          if (_error != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                  color: c.dangerWash,
                  borderRadius: BorderRadius.circular(12)),
              child: Row(
                children: [
                  Icon(Icons.error_outline, size: 18, color: c.danger),
                  const SizedBox(width: 10),
                  Expanded(
                      child: Text(_error!,
                          style: AppType.label(c, color: c.danger))),
                ],
              ),
            ),
          ],
          const SizedBox(height: 20),
          PrimaryButton(
            label: 'Submit application',
            loading: _submitting,
            onPressed: _submitting ? null : _submit,
          ),
        ],
      ),
    );
  }
}
