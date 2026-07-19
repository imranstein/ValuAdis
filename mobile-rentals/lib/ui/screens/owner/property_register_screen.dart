import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:image_picker/image_picker.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/owner_listing.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../widgets/band_range_bar.dart';
import '../../widgets/buttons.dart';
import '../../widgets/inputs.dart';
import '../../widgets/pressable.dart';

/// Owner registers a property and submits it for rent in one flow: create the
/// property, then create the listing (which triggers an automatic rent
/// valuation and returns the suggested band).
class PropertyRegisterScreen extends StatefulWidget {
  const PropertyRegisterScreen({super.key, required this.repo});
  final RentalsRepository repo;

  @override
  State<PropertyRegisterScreen> createState() => _PropertyRegisterScreenState();
}

class _PropertyRegisterScreenState extends State<PropertyRegisterScreen> {
  final _address = TextEditingController();
  final _area = TextEditingController();
  final _year = TextEditingController();
  final _notes = TextEditingController();

  String _subCity = AppConstants.addisSubCities.first;
  String _type = AppConstants.propertyTypes.first;
  String? _subtype = AppConstants.subtypesByType['residential']!.first;
  String? _condition;
  int _bedrooms = 2;
  int _bathrooms = 1;
  LatLng? _pin;
  final List<XFile> _photos = [];

  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    for (final ctrl in [_address, _area, _year, _notes]) {
      ctrl.dispose();
    }
    super.dispose();
  }

  List<String> get _subtypes =>
      AppConstants.subtypesByType[_type] ?? const [];

  String? _validate() {
    if (_address.text.trim().length < 5) {
      return 'Enter the full property address (at least 5 characters).';
    }
    final area = double.tryParse(_area.text.trim());
    if (area == null || area <= 0) return 'Enter the area in square metres.';
    return null;
  }

  Future<void> _pickPhotos() async {
    final remaining = AppConstants.maxPhotosPerProperty - _photos.length;
    if (remaining <= 0) {
      setState(() => _error =
          'A property may have at most ${AppConstants.maxPhotosPerProperty} photos.');
      return;
    }
    List<XFile> picked;
    try {
      picked = await ImagePicker().pickMultiImage(imageQuality: 85);
    } catch (_) {
      // Picker unavailable (e.g. no gallery on this device); ignore silently.
      return;
    }
    if (picked.isEmpty) return;

    final accepted = <XFile>[];
    var oversized = 0;
    for (final file in picked.take(remaining)) {
      final size = await file.length();
      if (size > AppConstants.maxPhotoSizeBytes) {
        oversized++;
      } else {
        accepted.add(file);
      }
    }
    setState(() {
      _photos.addAll(accepted);
      if (oversized > 0) {
        final maxMb = AppConstants.maxPhotoSizeBytes ~/ (1024 * 1024);
        _error = oversized == 1
            ? 'One photo was over ${maxMb}MB and was not added.'
            : '$oversized photos were over ${maxMb}MB and were not added.';
      } else if (picked.length > remaining) {
        _error =
            'Only the first $remaining photos were added (${AppConstants.maxPhotosPerProperty} max).';
      }
    });
  }

  Future<void> _submit() async {
    final error = _validate();
    setState(() => _error = error);
    if (error != null) return;

    setState(() => _submitting = true);
    try {
      final payload = <String, dynamic>{
        'address': _address.text.trim(),
        'municipality': 'Addis Ababa',
        'subcity': _subCity,
        'property_type': _type,
        if (_subtype != null) 'property_subtype': _subtype,
        'area_sqm': double.parse(_area.text.trim()),
        'number_of_bedrooms': _bedrooms,
        'number_of_bathrooms': _bathrooms,
        if (_condition != null) 'condition': _condition,
        if (_year.text.trim().isNotEmpty)
          'year_built': int.tryParse(_year.text.trim()),
        if (_pin != null) 'latitude': _pin!.latitude,
        if (_pin != null) 'longitude': _pin!.longitude,
      };
      final propertyId = await widget.repo.createProperty(payload);
      final listing = await widget.repo.createListing(
          propertyId, _notes.text.trim().isEmpty ? null : _notes.text.trim());
      final failedPhotos = await _uploadPhotos(propertyId);
      if (!mounted) return;
      await _showResult(listing, failedPhotos);
      if (mounted) Navigator.of(context).pop(true);
    } on RentalsException catch (e) {
      setState(() {
        _error = e.message;
        _submitting = false;
      });
    }
  }

  /// Uploads picked photos now that the property has an id. Best-effort: the
  /// property and listing already exist, so a photo failure is surfaced in
  /// the result sheet rather than rolling back the submission.
  Future<int> _uploadPhotos(int propertyId) async {
    var failed = 0;
    for (final photo in _photos) {
      try {
        await widget.repo.uploadPropertyPhoto(propertyId, photo);
      } on RentalsException {
        failed++;
      }
    }
    return failed;
  }

  Future<void> _showResult(OwnerListing listing, int failedPhotoCount) {
    final c = AppColors.of(context);
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: c.surface,
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 22, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration:
                  BoxDecoration(color: c.greenSoft, shape: BoxShape.circle),
              child: Icon(Icons.check_rounded, color: c.green, size: 30),
            ),
            const SizedBox(height: 16),
            Text('Submitted for review', style: AppType.title(c)),
            const SizedBox(height: 6),
            Text(
              'A rental officer will verify the details and publish your listing '
              'at the band below.',
              style: AppType.body(c, color: c.inkMuted),
            ),
            const SizedBox(height: 20),
            BandRangeBar(band: listing.band),
            if (failedPhotoCount > 0) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                    color: c.goldWash, borderRadius: BorderRadius.circular(12)),
                child: Text(
                  failedPhotoCount == 1
                      ? 'One photo could not be uploaded. Add it from Manage '
                          'photos on this listing.'
                      : '$failedPhotoCount photos could not be uploaded. Add '
                          'them from Manage photos on this listing.',
                  style: AppType.label(c, color: c.inkSecondary),
                ),
              ),
            ],
            const SizedBox(height: 24),
            PrimaryButton(
                label: 'Done', onPressed: () => Navigator.of(context).pop()),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(title: const Text('Register a property')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
          children: [
            _section(c, 'Location'),
            AppTextField(
                label: 'Address',
                controller: _address,
                hint: 'Building, street, area',
                prefixIcon: Icons.place_outlined),
            const SizedBox(height: 14),
            AppDropdownField<String>(
              label: 'Sub-city',
              value: _subCity,
              items: AppConstants.addisSubCities,
              onChanged: (v) => setState(() => _subCity = v ?? _subCity),
            ),
            const SizedBox(height: 14),
            _MapPin(
                pin: _pin, onTap: (p) => setState(() => _pin = p)),
            const SizedBox(height: 24),
            _section(c, 'Property'),
            Row(
              children: [
                Expanded(
                  child: AppDropdownField<String>(
                    label: 'Type',
                    value: _type,
                    items: AppConstants.propertyTypes,
                    onChanged: (v) => setState(() {
                      _type = v ?? _type;
                      _subtype = _subtypes.isEmpty ? null : _subtypes.first;
                    }),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: AppDropdownField<String?>(
                    label: 'Subtype',
                    value: _subtype,
                    items: _subtypes,
                    onChanged: (v) => setState(() => _subtype = v),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: AppTextField(
                    label: 'Area (m2)',
                    controller: _area,
                    keyboardType: TextInputType.number,
                    prefixIcon: Icons.straighten_outlined,
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(RegExp(r'[0-9.]'))
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: AppTextField(
                    label: 'Year built',
                    controller: _year,
                    keyboardType: TextInputType.number,
                    hint: 'Optional',
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _Stepper(
                label: 'Bedrooms',
                value: _bedrooms,
                onChanged: (v) => setState(() => _bedrooms = v)),
            const SizedBox(height: 10),
            _Stepper(
                label: 'Bathrooms',
                value: _bathrooms,
                onChanged: (v) => setState(() => _bathrooms = v)),
            const SizedBox(height: 16),
            AppDropdownField<String?>(
              label: 'Condition',
              value: _condition,
              hint: 'Select condition',
              items: AppConstants.conditions,
              onChanged: (v) => setState(() => _condition = v),
            ),
            const SizedBox(height: 24),
            _section(c, 'Photos'),
            _PhotoPicker(
                photos: _photos,
                onAdd: _pickPhotos,
                onRemove: (i) => setState(() => _photos.removeAt(i))),
            const SizedBox(height: 24),
            _section(c, 'Note to the officer'),
            AppTextField(
                label: 'Optional message',
                controller: _notes,
                hint: 'Anything the reviewer should know',
                maxLines: 3),
            if (_error != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                    color: c.dangerWash,
                    borderRadius: BorderRadius.circular(12)),
                child: Row(children: [
                  Icon(Icons.error_outline, size: 18, color: c.danger),
                  const SizedBox(width: 10),
                  Expanded(
                      child: Text(_error!,
                          style: AppType.label(c, color: c.danger))),
                ]),
              ),
            ],
            const SizedBox(height: 24),
            PrimaryButton(
              label: 'Submit for review',
              loading: _submitting,
              onPressed: _submitting ? null : _submit,
            ),
          ],
        ),
      ),
    );
  }

  Widget _section(AppColors c, String title) => Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Text(title.toUpperCase(),
            style: AppType.caption(c, color: c.inkMuted)
                .copyWith(fontWeight: FontWeight.w700, letterSpacing: 1)),
      );
}

class _Stepper extends StatelessWidget {
  const _Stepper(
      {required this.label, required this.value, required this.onChanged});
  final String label;
  final int value;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    Widget btn(IconData icon, VoidCallback? onTap) => Pressable(
          onTap: onTap,
          scale: 0.9,
          child: Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
                color: c.surfaceSunken.withValues(alpha: 0.6),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: c.border)),
            child: Icon(icon,
                size: 18, color: onTap == null ? c.inkMuted : c.ink),
          ),
        );
    return Row(
      children: [
        Expanded(
            child: Text(label, style: AppType.label(c, color: c.inkSecondary))),
        btn(Icons.remove, value > 0 ? () => onChanged(value - 1) : null),
        SizedBox(
          width: 40,
          child: Center(
            child: Text('$value',
                style: AppType.mono(c, size: 17, weight: FontWeight.w700)),
          ),
        ),
        btn(Icons.add, value < 20 ? () => onChanged(value + 1) : null),
      ],
    );
  }
}

class _MapPin extends StatelessWidget {
  const _MapPin({required this.pin, required this.onTap});
  final LatLng? pin;
  final ValueChanged<LatLng> onTap;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Map pin  (tap to place)',
            style: AppType.label(c, color: c.inkSecondary)),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: SizedBox(
            height: 170,
            child: FlutterMap(
              options: MapOptions(
                initialCenter: pin ??
                    const LatLng(
                        AppConstants.defaultLat, AppConstants.defaultLon),
                initialZoom: 13,
                onTap: (_, point) => onTap(point),
              ),
              children: [
                TileLayer(
                  urlTemplate:
                      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.valuadis.rent',
                ),
                if (pin != null)
                  MarkerLayer(markers: [
                    Marker(
                      point: pin!,
                      width: 40,
                      height: 40,
                      child: Icon(Icons.location_on,
                          color: c.green, size: 36),
                    ),
                  ]),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _PhotoPicker extends StatelessWidget {
  const _PhotoPicker(
      {required this.photos, required this.onAdd, required this.onRemove});
  final List<XFile> photos;
  final VoidCallback onAdd;
  final ValueChanged<int> onRemove;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          height: 88,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              Pressable(
                onTap: onAdd,
                child: Container(
                  width: 88,
                  margin: const EdgeInsets.only(right: 10),
                  decoration: BoxDecoration(
                    color: c.surfaceSunken.withValues(alpha: 0.5),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: c.border),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.add_a_photo_outlined,
                          color: c.green, size: 22),
                      const SizedBox(height: 4),
                      Text('Add', style: AppType.caption(c, color: c.inkMuted)),
                    ],
                  ),
                ),
              ),
              for (var i = 0; i < photos.length; i++)
                Stack(
                  children: [
                    Container(
                      width: 88,
                      height: 88,
                      margin: const EdgeInsets.only(right: 10),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        image: DecorationImage(
                            image: FileImage(File(photos[i].path)),
                            fit: BoxFit.cover),
                      ),
                    ),
                    Positioned(
                      top: 4,
                      right: 14,
                      child: Pressable(
                        onTap: () => onRemove(i),
                        child: Container(
                          padding: const EdgeInsets.all(3),
                          decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.5),
                              shape: BoxShape.circle),
                          child: const Icon(Icons.close,
                              size: 13, color: Colors.white),
                        ),
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Photos upload to the registry when you submit. JPG, PNG or WEBP, '
          'up to ${AppConstants.maxPhotoSizeBytes ~/ (1024 * 1024)}MB each, '
          '${AppConstants.maxPhotosPerProperty} max.',
          style: AppType.caption(c, color: c.inkMuted).copyWith(height: 1.4),
        ),
      ],
    );
  }
}
