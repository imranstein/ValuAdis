import 'package:flutter/material.dart';

import '../../data/models/property.dart';
import '../../core/utils.dart';
import '../theme/app_theme.dart';
import 'shared_ui.dart';

class PropertyCard extends StatelessWidget {
  final Property property;
  final VoidCallback onTap;

  const PropertyCard({
    super.key,
    required this.property,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: InkWell(
        onTap: onTap,
        borderRadius: AppRadius.smRadius,
        child: Semantics(
          button: true,
          label: 'Open property ${property.address}',
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Icon(
                Icons.home_outlined,
                color: Theme.of(context).colorScheme.onPrimaryContainer,
              ),
            ),
            title: Text(
              property.address,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 4),
                Text(
                  '${property.propertyType} • ${AppUtils.formatArea(property.areaSqm)}',
                ),
                const SizedBox(height: 8),
                AppStatusChip.fromStatus(
                  context,
                  property.syncStatus,
                ),
              ],
            ),
            isThreeLine: true,
            trailing: const Icon(Icons.chevron_right),
          ),
        ),
      ),
    );
  }
}
