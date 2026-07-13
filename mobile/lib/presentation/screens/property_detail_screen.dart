import 'dart:io';
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';

import '../../bloc/property/property_bloc.dart';
import '../../bloc/property/property_event.dart';
import '../../bloc/property/property_state.dart';
import '../../bloc/sync/sync_bloc.dart';
import '../../bloc/sync/sync_state.dart';
import '../../bloc/valuation/valuation_bloc.dart';
import '../../bloc/valuation/valuation_event.dart';
import '../../bloc/valuation/valuation_state.dart';
import '../../core/utils.dart';
import '../../data/models/photo.dart';
import '../../data/models/property.dart';
import '../../presentation/bloc_providers.dart';
import '../theme/app_theme.dart';
import '../widgets/shared_ui.dart';

class PropertyDetailScreen extends StatefulWidget {
  static const String routeName = '/property-detail';

  final Property property;

  const PropertyDetailScreen({
    super.key,
    required this.property,
  });

  @override
  State<PropertyDetailScreen> createState() => _PropertyDetailScreenState();
}

class _PropertyDetailScreenState extends State<PropertyDetailScreen> {
  final ImagePicker _imagePicker = ImagePicker();
  final TextEditingController _marketValueController = TextEditingController();
  final TextEditingController _taxableValueController = TextEditingController();
  int? _loadedValuationsForProperty;
  int? _loadedPhotosForProperty;
  bool _isDetailLoading = false;

  List<Photo> _photos = const [];
  bool _photosLoading = false;

  @override
  void initState() {
    super.initState();
    final propertyId = widget.property.id;
    if (propertyId != null) {
      unawaited(_loadPropertyDetailData(propertyId));
    }
  }

  @override
  void didUpdateWidget(covariant PropertyDetailScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.property.id != oldWidget.property.id &&
        widget.property.id != null) {
      unawaited(_loadPropertyDetailData(widget.property.id!));
    }
  }

  @override
  void dispose() {
    _marketValueController.dispose();
    _taxableValueController.dispose();
    super.dispose();
  }

  Future<void> _openEditDialog(
      BuildContext context, Property currentProperty) async {
    final propertyBloc = context.read<PropertyBloc>();
    final address = TextEditingController(text: currentProperty.address);
    final propertyType =
        TextEditingController(text: currentProperty.propertyType);
    final area =
        TextEditingController(text: currentProperty.areaSqm.toStringAsFixed(2));

    final updated = await showDialog<Property>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Edit property'),
          content: SizedBox(
            width: 360,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: address,
                  key: const Key('edit-address-field'),
                  decoration: const InputDecoration(labelText: 'Address'),
                ),
                const SizedBox(height: AppSpacing.md),
                TextField(
                  controller: propertyType,
                  key: const Key('edit-type-field'),
                  decoration: const InputDecoration(labelText: 'Property type'),
                ),
                const SizedBox(height: AppSpacing.md),
                TextField(
                  controller: area,
                  key: const Key('edit-area-field'),
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Area (sqm)'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () {
                final parsedArea = double.tryParse(area.text.trim()) ??
                    currentProperty.areaSqm;
                final newProperty = currentProperty.copyWith(
                  address: address.text.trim(),
                  propertyType: propertyType.text.trim(),
                  areaSqm: parsedArea,
                );
                Navigator.of(dialogContext).pop(newProperty);
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    );

    if (!mounted || updated == null) {
      return;
    }
    final withPendingStatus = updated.copyWith(
      syncStatus: 'pending',
      updatedAt: DateTime.now().toIso8601String(),
    );
    propertyBloc.add(UpdateProperty(withPendingStatus));
    propertyBloc.add(LoadProperties());
  }

  Future<void> _openValuationDialog(
    BuildContext context,
    Property currentProperty,
  ) async {
    final valuationBloc = context.read<ValuationBloc>();
    _marketValueController.clear();
    _taxableValueController.clear();

    if (currentProperty.id == null) {
      return;
    }

    final created = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Add valuation'),
          content: SizedBox(
            width: 360,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _marketValueController,
                  key: const Key('valuation-market-field'),
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Market value'),
                ),
                const SizedBox(height: AppSpacing.md),
                TextField(
                  controller: _taxableValueController,
                  key: const Key('valuation-taxable-field'),
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Taxable value'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () {
                final marketValue =
                    double.tryParse(_marketValueController.text.trim()) ?? 0;
                final taxableValue =
                    double.tryParse(_taxableValueController.text.trim()) ?? 0;
                context.read<ValuationBloc>().add(
                      CreateNextValuation(
                        propertyId: currentProperty.id!,
                        marketValue: marketValue,
                        taxableValue: taxableValue,
                      ),
                    );
                Navigator.of(dialogContext).pop(true);
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    );

    if (!mounted || created != true || currentProperty.id == null) {
      return;
    }
    if (!mounted) {
      return;
    }

    _loadedValuationsForProperty = null;
    valuationBloc.add(LoadValuations(currentProperty.id!));
  }

  Future<void> _attachPhoto(Property currentProperty) async {
    if (currentProperty.id == null) {
      return;
    }

    final file = await _imagePicker.pickImage(source: ImageSource.camera);
    if (file == null || !mounted) {
      return;
    }

    setState(() {
      _photosLoading = true;
    });
    await blocProviders.photoRepository.addPhoto(
      Photo(
        propertyId: currentProperty.id!,
        filePath: file.path,
        createdAt: DateTime.now().toIso8601String(),
      ),
    );
    await _loadPhotos(currentProperty.id!, forceReload: true);
    if (mounted) {
      setState(() {
        _photosLoading = false;
      });
    }
  }

  Future<void> _loadPhotos(
    int propertyId, {
    bool forceReload = false,
  }) async {
    if (_photosLoading && !forceReload) {
      return;
    }

    setState(() {
      _photosLoading = true;
    });
    try {
      final photos =
          await blocProviders.photoRepository.getPhotosForProperty(propertyId);
      if (mounted) {
        setState(() {
          _photos = photos;
          _photosLoading = false;
          _loadedPhotosForProperty = propertyId;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _photos = const [];
          _photosLoading = false;
          _loadedPhotosForProperty = propertyId;
        });
      }
    }
  }

  Future<void> _loadPropertyDetailData(int propertyId) async {
    if (_isDetailLoading) {
      return;
    }

    _isDetailLoading = true;
    if (mounted) {
      if (_loadedValuationsForProperty != propertyId) {
        context.read<ValuationBloc>().add(LoadValuations(propertyId));
        _loadedValuationsForProperty = propertyId;
      }
      try {
        await _loadPhotos(propertyId);
      } finally {
        _isDetailLoading = false;
      }
    } else {
      _isDetailLoading = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<PropertyBloc, PropertyState>(
      builder: (context, propertyState) {
        final current = propertyState.properties.isEmpty
            ? widget.property
            : propertyState.properties.firstWhere(
                (propertyItem) => propertyItem.id == widget.property.id,
                orElse: () => widget.property,
              );
        if (current.id != null &&
            (_loadedPhotosForProperty != current.id ||
                _loadedValuationsForProperty != current.id)) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (!mounted) return;
            unawaited(_loadPropertyDetailData(current.id!));
          });
        }

        return Scaffold(
          appBar: AppBar(
            title: const Text('Property detail'),
            actions: [
              IconButton(
                icon: const Icon(Icons.photo_camera_outlined),
                tooltip: 'Attach photo',
                onPressed: () => _attachPhoto(current),
              ),
              IconButton(
                icon: const Icon(Icons.attach_money_outlined),
                tooltip: 'Add valuation',
                onPressed: () => _openValuationDialog(context, current),
              ),
              IconButton(
                icon: const Icon(Icons.edit_outlined),
                tooltip: 'Edit property',
                onPressed: () => _openEditDialog(context, current),
              ),
            ],
          ),
          body: BlocBuilder<SyncBloc, SyncState>(
            builder: (context, syncState) {
              return BlocBuilder<ValuationBloc, ValuationState>(
                builder: (context, valuationState) {
                  return Column(
                    children: [
                      AppSyncBanner(syncState: syncState),
                      Expanded(
                        child: ListView(
                          padding: const EdgeInsets.all(AppSpacing.lg),
                          children: [
                            AppCard(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  AppSectionHeader(
                                    title: current.address,
                                    subtitle: current.propertyType,
                                    trailing: AppStatusChip.fromStatus(
                                      context,
                                      current.syncStatus,
                                      label: AppUtils.syncStatusLabel(
                                          current.syncStatus),
                                    ),
                                  ),
                                  const SizedBox(height: AppSpacing.md),
                                  Text(
                                    'Area',
                                    style: Theme.of(context)
                                        .textTheme
                                        .bodySmall
                                        ?.copyWith(
                                          color: Theme.of(context)
                                              .colorScheme
                                              .onSurfaceVariant,
                                        ),
                                  ),
                                  const SizedBox(height: AppSpacing.xs),
                                  Text(
                                    AppUtils.formatArea(current.areaSqm),
                                    style:
                                        Theme.of(context).textTheme.titleMedium,
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: AppSpacing.md),
                            if (current.boundary == null ||
                                current.boundary!.isEmpty)
                              const AppEmptyState(
                                icon: Icons.map_outlined,
                                title: 'Boundary not set',
                                message:
                                    'Draw a boundary on the map before valuation.',
                              )
                            else
                              AppCard(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Boundary',
                                      style: Theme.of(context).textTheme.titleMedium,
                                    ),
                                    const SizedBox(height: AppSpacing.xs),
                                    Text(current.boundary!),
                                  ],
                                ),
                              ),
                            const SizedBox(height: AppSpacing.md),
                            if (_photosLoading)
                              const AppLoadingState(
                                  message: 'Loading photos...')
                            else if (_photos.isEmpty)
                              const AppEmptyState(
                                icon: Icons.photo_library_outlined,
                                title: 'No photos yet',
                                message:
                                    'Attach photos to keep field evidence with this property.',
                              )
                            else
                              AppCard(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Photos',
                                      style: Theme.of(context).textTheme.titleMedium,
                                    ),
                                    const SizedBox(height: AppSpacing.sm),
                                    SizedBox(
                                      height: 130,
                                      child: ListView.separated(
                                        scrollDirection: Axis.horizontal,
                                        itemCount: _photos.length,
                                        separatorBuilder: (context, index) =>
                                            const SizedBox(
                                          width: AppSpacing.sm,
                                        ),
                                        itemBuilder: (context, index) {
                                          final photo = _photos[index];
                                          return ClipRRect(
                                            borderRadius: AppRadius.smRadius,
                                            child: Image.file(
                                              File(photo.filePath),
                                              width: 120,
                                              fit: BoxFit.cover,
                                              errorBuilder: (context, error,
                                                      stackTrace) =>
                                                  const SizedBox(
                                                width: 120,
                                                child: Center(
                                                  child: Icon(Icons.image),
                                                ),
                                              ),
                                            ),
                                          );
                                        },
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            const SizedBox(height: AppSpacing.md),
                            if (valuationState.valuations.isNotEmpty) ...[
                              AppCard(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    AppSectionHeader(
                                      title: 'Latest valuation',
                                      subtitle:
                                          'Updated ${valuationState.valuations.first.createdAt}',
                                    ),
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            'Market: ${valuationState.valuations.first.marketValue.toStringAsFixed(2)}',
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodyLarge,
                                          ),
                                        ),
                                        Expanded(
                                          child: Text(
                                            'Taxable: ${valuationState.valuations.first.taxableValue.toStringAsFixed(2)}',
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodyLarge,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: AppSpacing.md),
                              AppCard(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Valuation history',
                                      style: Theme.of(context).textTheme.titleMedium,
                                    ),
                                    const SizedBox(height: AppSpacing.sm),
                                    ...valuationState.valuations.map(
                                      (valuation) => Padding(
                                        padding: const EdgeInsets.only(
                                          bottom: AppSpacing.xs,
                                        ),
                                        child: Text(
                                          '${valuation.createdAt}: market ${valuation.marketValue.toStringAsFixed(2)}, taxable ${valuation.taxableValue.toStringAsFixed(2)}',
                                          style:
                                              Theme.of(context).textTheme.bodySmall,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ] else
                              const AppEmptyState(
                                icon: Icons.receipt_long_outlined,
                                title: 'No valuations yet',
                                message:
                                    'Add a valuation to capture market and taxable values.',
                              ),
                            const SizedBox(height: AppSpacing.md),
                            Text(
                              'Created ${current.createdAt}',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            const SizedBox(height: AppSpacing.xs),
                            Text(
                              'Updated ${current.updatedAt}',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                },
              );
            },
          ),
        );
      },
    );
  }
}

class PropertyDetailScreenArgs {
  final Property property;

  const PropertyDetailScreenArgs(this.property);
}
