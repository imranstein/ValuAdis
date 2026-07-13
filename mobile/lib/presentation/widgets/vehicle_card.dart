import 'package:flutter/material.dart';

import '../../data/models/vehicle.dart';
import '../theme/app_theme.dart';
import 'shared_ui.dart';

class VehicleCard extends StatelessWidget {
  final Vehicle vehicle;
  final VoidCallback onTap;

  const VehicleCard({
    super.key,
    required this.vehicle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final location = [vehicle.city, vehicle.region]
        .where((value) => value != null && value.isNotEmpty)
        .join(', ');

    return AppCard(
      child: InkWell(
        onTap: onTap,
        borderRadius: AppRadius.smRadius,
        child: Semantics(
          button: true,
          label: 'Open vehicle ${vehicle.displayName}',
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Icon(
                Icons.directions_car_outlined,
                color: Theme.of(context).colorScheme.onPrimaryContainer,
              ),
            ),
            title: Text(
              vehicle.displayName,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 4),
                Text('Plate ${vehicle.plateNumber}'),
                if (location.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(location),
                ],
              ],
            ),
            isThreeLine: location.isNotEmpty,
            trailing: const Icon(Icons.chevron_right),
          ),
        ),
      ),
    );
  }
}
