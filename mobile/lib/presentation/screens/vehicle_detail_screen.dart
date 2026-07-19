import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/vehicle/vehicle_bloc.dart';
import '../../bloc/vehicle/vehicle_event.dart';
import '../../bloc/vehicle/vehicle_state.dart';
import '../../data/models/vehicle.dart';
import '../theme/app_theme.dart';
import '../widgets/shared_ui.dart';

class VehicleDetailScreen extends StatefulWidget {
  static const String routeName = '/vehicle-detail';

  final Vehicle vehicle;

  const VehicleDetailScreen({super.key, required this.vehicle});

  @override
  State<VehicleDetailScreen> createState() => _VehicleDetailScreenState();
}

class _VehicleDetailScreenState extends State<VehicleDetailScreen> {
  @override
  void initState() {
    super.initState();
    // Refresh from GET /vehicles/{id} so the detail reflects backend state.
    context.read<VehicleBloc>().add(LoadVehicleDetail(widget.vehicle.id));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Vehicle detail')),
      body: BlocBuilder<VehicleBloc, VehicleState>(
        builder: (context, state) {
          final vehicle = (state.selected != null &&
                  state.selected!.id == widget.vehicle.id)
              ? state.selected!
              : widget.vehicle;
          final isLoading =
              state.detailStatus == VehicleDetailStatus.loading;

          return ListView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            children: [
              if (isLoading)
                const Padding(
                  padding: EdgeInsets.only(bottom: AppSpacing.md),
                  child: LinearProgressIndicator(),
                ),
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    AppSectionHeader(
                      title: vehicle.displayName,
                      subtitle: 'Plate ${vehicle.plateNumber}',
                    ),
                    _DetailRow(label: 'VIN', value: vehicle.vin),
                    _DetailRow(label: 'Make', value: vehicle.make),
                    _DetailRow(label: 'Model', value: vehicle.model),
                    _DetailRow(label: 'Year', value: '${vehicle.year}'),
                    if (vehicle.bodyType != null)
                      _DetailRow(label: 'Body type', value: vehicle.bodyType!),
                    if (vehicle.fuelType != null)
                      _DetailRow(label: 'Fuel', value: vehicle.fuelType!),
                    if (vehicle.transmission != null)
                      _DetailRow(
                          label: 'Transmission',
                          value: vehicle.transmission!),
                    if (vehicle.engineCapacity != null)
                      _DetailRow(
                          label: 'Engine',
                          value: '${vehicle.engineCapacity} cc'),
                    if (vehicle.mileage != null)
                      _DetailRow(
                          label: 'Mileage', value: '${vehicle.mileage} km'),
                    if (vehicle.color != null)
                      _DetailRow(label: 'Color', value: vehicle.color!),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ethiopian details',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: AppSpacing.sm),
                    if (vehicle.region != null)
                      _DetailRow(label: 'Region', value: vehicle.region!),
                    if (vehicle.city != null)
                      _DetailRow(label: 'City', value: vehicle.city!),
                    if (vehicle.importYear != null)
                      _DetailRow(
                          label: 'Import year',
                          value: '${vehicle.importYear}'),
                    _DetailRow(
                      label: 'Customs duty',
                      value: vehicle.customDutyPaid ? 'Paid' : 'Not paid',
                    ),
                    _DetailRow(
                      label: 'Previous owners',
                      value: '${vehicle.previousOwners}',
                    ),
                  ],
                ),
              ),
              if (state.detailStatus == VehicleDetailStatus.error) ...[
                const SizedBox(height: AppSpacing.md),
                AppEmptyState(
                  icon: Icons.cloud_off,
                  title: 'Could not refresh vehicle',
                  message: state.message ??
                      'Showing the last known details for this vehicle.',
                  actionLabel: 'Retry',
                  onAction: () => context
                      .read<VehicleBloc>()
                      .add(LoadVehicleDetail(widget.vehicle.id)),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}

class VehicleDetailScreenArgs {
  final Vehicle vehicle;

  const VehicleDetailScreenArgs(this.vehicle);
}
