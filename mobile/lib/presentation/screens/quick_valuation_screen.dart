import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/quick_valuation/quick_valuation_bloc.dart';
import '../../bloc/quick_valuation/quick_valuation_event.dart';
import '../../bloc/quick_valuation/quick_valuation_state.dart';
import '../../data/models/quick_valuation.dart';
import '../theme/app_theme.dart';
import '../widgets/shared_ui.dart';

/// Option values MUST match the backend valuation service keys exactly
/// (`backend/app/modules/valuation/services.py`).
const List<String> _municipalities = [
  'Addis Ababa',
  'Dire Dawa',
  'Mekelle',
  'Bahir Dar',
  'Adama',
  'Hawassa',
  'Gonder',
  'Jimma',
  'Dessie',
  'Jijiga',
  'Shashamane',
  'Arba Minch',
  'Harar',
  'Nekemte',
  'Debre Markos',
  'Debre Birhan',
];

const Map<String, String> _propertyTypes = {
  'residential': 'Residential',
  'commercial': 'Commercial',
  'industrial': 'Industrial',
  'agricultural': 'Agricultural',
  'mixed_use': 'Mixed use',
};

const Map<String, String> _conditions = {
  'excellent': 'Excellent',
  'good': 'Good',
  'fair': 'Fair',
  'poor': 'Poor',
};

const Map<String, String> _neighborhoods = {
  'prime': 'Prime',
  'above_average': 'Above average',
  'average': 'Average',
  'below_average': 'Below average',
  'developing': 'Developing',
};

class QuickValuationScreen extends StatefulWidget {
  final bool showAppBar;

  const QuickValuationScreen({super.key, this.showAppBar = true});

  @override
  State<QuickValuationScreen> createState() => _QuickValuationScreenState();
}

class _QuickValuationScreenState extends State<QuickValuationScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _areaController = TextEditingController();

  String _municipality = _municipalities.first;
  String _propertyType = 'residential';
  String _condition = 'good';
  String _neighborhood = 'average';

  @override
  void dispose() {
    _areaController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }
    final area = double.parse(_areaController.text.trim());
    context.read<QuickValuationBloc>().add(
          QuickValuationRequested(
            QuickValuationRequest(
              municipality: _municipality,
              areaSqm: area,
              propertyType: _propertyType,
              condition: _condition,
              neighborhoodQuality: _neighborhood,
            ),
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    final body = BlocBuilder<QuickValuationBloc, QuickValuationState>(
      builder: (context, state) {
        final isLoading = state.status == QuickValuationStatus.loading;

        return ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            Form(
              key: _formKey,
              child: AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Quick valuation',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: AppSpacing.md),
                    DropdownButtonFormField<String>(
                      key: const Key('quick-municipality-field'),
                      initialValue: _municipality,
                      decoration:
                          const InputDecoration(labelText: 'Municipality'),
                      items: _municipalities
                          .map(
                            (value) => DropdownMenuItem(
                              value: value,
                              child: Text(value),
                            ),
                          )
                          .toList(),
                      onChanged: (value) =>
                          setState(() => _municipality = value ?? _municipality),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    TextFormField(
                      controller: _areaController,
                      key: const Key('quick-area-field'),
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                      decoration:
                          const InputDecoration(labelText: 'Area (sqm)'),
                      validator: (value) {
                        final parsed = double.tryParse(value?.trim() ?? '');
                        if (parsed == null || parsed <= 0) {
                          return 'Enter an area greater than 0';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _MappedDropdown(
                      fieldKey: const Key('quick-property-type-field'),
                      label: 'Property type',
                      value: _propertyType,
                      options: _propertyTypes,
                      onChanged: (value) =>
                          setState(() => _propertyType = value),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _MappedDropdown(
                      fieldKey: const Key('quick-condition-field'),
                      label: 'Condition',
                      value: _condition,
                      options: _conditions,
                      onChanged: (value) => setState(() => _condition = value),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _MappedDropdown(
                      fieldKey: const Key('quick-neighborhood-field'),
                      label: 'Neighborhood quality',
                      value: _neighborhood,
                      options: _neighborhoods,
                      onChanged: (value) =>
                          setState(() => _neighborhood = value),
                    ),
                    const SizedBox(height: AppSpacing.lg),
                    FilledButton(
                      key: const Key('quick-submit-button'),
                      onPressed: isLoading ? null : _submit,
                      child: isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Calculate valuation'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            if (state.status == QuickValuationStatus.failure)
              AppEmptyState(
                icon: Icons.error_outline,
                title: 'Valuation failed',
                message: state.message ??
                    'Could not calculate valuation. Check your input.',
              )
            else if (state.status == QuickValuationStatus.success &&
                state.result != null)
              _ResultCard(result: state.result!),
          ],
        );
      },
    );

    if (!widget.showAppBar) {
      return body;
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Quick valuation')),
      body: body,
    );
  }
}

class _MappedDropdown extends StatelessWidget {
  final Key fieldKey;
  final String label;
  final String value;
  final Map<String, String> options;
  final ValueChanged<String> onChanged;

  const _MappedDropdown({
    required this.fieldKey,
    required this.label,
    required this.value,
    required this.options,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      key: fieldKey,
      initialValue: value,
      decoration: InputDecoration(labelText: label),
      items: options.entries
          .map(
            (entry) => DropdownMenuItem(
              value: entry.key,
              child: Text(entry.value),
            ),
          )
          .toList(),
      onChanged: (next) {
        if (next != null) onChanged(next);
      },
    );
  }
}

class _ResultCard extends StatelessWidget {
  final QuickValuationResult result;

  const _ResultCard({required this.result});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const AppSectionHeader(
            title: 'Estimated value',
            subtitle: 'Taxable value is 25% of market value',
          ),
          Row(
            children: [
              Expanded(
                child: _ValueBlock(
                  label: 'Market value',
                  value: result.marketValue,
                ),
              ),
              Expanded(
                child: _ValueBlock(
                  label: 'Taxable value',
                  value: result.taxableValue,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Base rate ${result.baseRate.toStringAsFixed(2)} ETB/sqm '
            '• multiplier ${result.multiplier.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
        ],
      ),
    );
  }
}

class _ValueBlock extends StatelessWidget {
  final String label;
  final double value;

  const _ValueBlock({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          '${value.toStringAsFixed(2)} ETB',
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ],
    );
  }
}
