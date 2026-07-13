import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/vehicle/vehicle_bloc.dart';
import '../../bloc/vehicle/vehicle_event.dart';
import '../../bloc/vehicle/vehicle_state.dart';
import '../theme/app_theme.dart';
import '../widgets/shared_ui.dart';
import '../widgets/vehicle_card.dart';
import 'vehicle_detail_screen.dart';

class VehicleListScreen extends StatelessWidget {
  final bool showAppBar;

  const VehicleListScreen({super.key, this.showAppBar = true});

  @override
  Widget build(BuildContext context) {
    final body = BlocBuilder<VehicleBloc, VehicleState>(
      builder: (context, state) {
        if (state.status == VehicleStatus.loading && state.vehicles.isEmpty) {
          return const AppLoadingState(message: 'Loading vehicles...');
        }

        if (state.status == VehicleStatus.error && state.vehicles.isEmpty) {
          return AppEmptyState(
            icon: Icons.cloud_off,
            title: 'Could not load vehicles',
            message: state.message ?? 'Please retry to load the vehicle list.',
            actionLabel: 'Retry',
            onAction: () => context.read<VehicleBloc>().add(LoadVehicles()),
          );
        }

        if (state.vehicles.isEmpty) {
          return AppEmptyState(
            icon: Icons.directions_car_outlined,
            title: 'No vehicles yet',
            message: 'Vehicles registered on the backend appear here.',
            actionLabel: 'Refresh',
            onAction: () => context.read<VehicleBloc>().add(LoadVehicles()),
          );
        }

        return RefreshIndicator(
          onRefresh: () async =>
              context.read<VehicleBloc>().add(LoadVehicles()),
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(
              vertical: AppSpacing.sm,
              horizontal: AppSpacing.md,
            ),
            itemCount: state.vehicles.length,
            itemBuilder: (context, index) {
              final vehicle = state.vehicles[index];
              return VehicleCard(
                vehicle: vehicle,
                onTap: () => Navigator.of(context).pushNamed(
                  VehicleDetailScreen.routeName,
                  arguments: VehicleDetailScreenArgs(vehicle),
                ),
              );
            },
          ),
        );
      },
    );

    if (!showAppBar) {
      return body;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Vehicles'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh vehicles',
            onPressed: () => context.read<VehicleBloc>().add(LoadVehicles()),
          ),
        ],
      ),
      body: body,
    );
  }
}
