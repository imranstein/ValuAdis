import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/property/property_bloc.dart';
import '../../bloc/property/property_event.dart';
import '../../data/models/property.dart';
import '../widgets/shared_ui.dart';
import '../theme/app_theme.dart';
import 'map_screen.dart';

class PropertyCreateScreen extends StatefulWidget {
  final bool showAppBar;

  const PropertyCreateScreen({
    super.key,
    this.showAppBar = true,
  });

  @override
  State<PropertyCreateScreen> createState() => _PropertyCreateScreenState();
}

class _PropertyCreateScreenState extends State<PropertyCreateScreen> {
  static const List<String> _municipalities = [
    'Addis Ababa',
    'Dire Dawa',
    'Adama',
    'Bahir Dar',
    'Hawassa',
    'Mekelle',
    'Gondar',
  ];

  final _formKey = GlobalKey<FormState>();
  final _addressController = TextEditingController();
  final _propertyTypeController = TextEditingController(text: 'residential');
  String _municipality = 'Addis Ababa';
  String? _boundaryWkt;
  double _areaSqm = 0.0;

  @override
  void dispose() {
    _addressController.dispose();
    _propertyTypeController.dispose();
    super.dispose();
  }

  Future<void> _pickBoundary() async {
    final result = await Navigator.of(context).push<MapScreenResult>(
      MaterialPageRoute(builder: (_) => const MapScreen()),
    );
    if (result != null && mounted) {
      setState(() {
        _boundaryWkt = result.wkt;
        _areaSqm = result.areaSqm;
      });
    }
  }

  void _submit() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final address = _addressController.text.trim();
    final propertyType = _propertyTypeController.text.trim().isEmpty
        ? 'residential'
        : _propertyTypeController.text.trim();
    final now = DateTime.now().toIso8601String();
    final property = Property(
      address: address,
      municipality: _municipality,
      propertyType: propertyType,
      boundary: _boundaryWkt,
      areaSqm: _areaSqm > 0 ? _areaSqm : 0,
      syncStatus: 'pending',
      createdAt: now,
      updatedAt: now,
    );
    context.read<PropertyBloc>().add(CreateProperty(property));
    if (!mounted) return;
    if (Navigator.of(context).canPop()) {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Form(
        key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(AppSpacing.md),
        children: [
            if (widget.showAppBar) const SizedBox(height: AppSpacing.xxs),
            AppSectionHeader(
              title: 'New Property',
              subtitle: 'Capture property metadata, then draw a boundary.',
            ),
            AppCard(
              child: Column(
                children: [
                  TextFormField(
                    controller: _addressController,
                    decoration: const InputDecoration(
                      labelText: 'Address',
                      border: OutlineInputBorder(),
                      hintText: 'e.g. Bole, Addis Ababa',
                    ),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'Enter address' : null,
                  ),
                  const SizedBox(height: AppSpacing.md),
                  DropdownButtonFormField<String>(
                    initialValue: _municipality,
                    decoration: const InputDecoration(
                      labelText: 'Municipality',
                      border: OutlineInputBorder(),
                    ),
                    items: _municipalities
                        .map(
                          (name) => DropdownMenuItem(
                            value: name,
                            child: Text(name),
                          ),
                        )
                        .toList(),
                    onChanged: (value) {
                      if (value != null) {
                        setState(() => _municipality = value);
                      }
                    },
                  ),
                  const SizedBox(height: AppSpacing.md),
                  TextFormField(
                    controller: _propertyTypeController,
                    decoration: const InputDecoration(
                      labelText: 'Property type',
                      border: OutlineInputBorder(),
                      hintText: 'residential, commercial, etc.',
                    ),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  OutlinedButton.icon(
                    onPressed: _pickBoundary,
                    icon: const Icon(Icons.map_outlined),
                    label: Text(
                      _boundaryWkt != null
                          ? 'Boundary set (${_areaSqm.toStringAsFixed(0)} sqm)'
                          : 'Draw boundary on map',
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  FilledButton(
                    onPressed: _submit,
                    child: const Text('Save property'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
