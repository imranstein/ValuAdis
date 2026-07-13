import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/auth/auth_bloc.dart';
import '../../bloc/auth/auth_event.dart';
import '../../bloc/property/property_bloc.dart';
import '../../bloc/property/property_event.dart';
import '../../bloc/property/property_state.dart';
import '../../bloc/sync/sync_bloc.dart';
import '../../bloc/sync/sync_event.dart';
import '../../bloc/sync/sync_state.dart';
import '../../core/constants.dart';
import '../theme/app_theme.dart';
import '../widgets/property_card.dart';
import '../widgets/shared_ui.dart';
import 'map_screen.dart';
import 'property_create_screen.dart';
import 'property_detail_screen.dart';
import 'quick_valuation_screen.dart';
import 'vehicle_list_screen.dart';

class PropertyListScreen extends StatelessWidget {
  const PropertyListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const PropertyListShell();
  }
}

class PropertyListShell extends StatefulWidget {
  const PropertyListShell({super.key});

  @override
  State<PropertyListShell> createState() => _PropertyListShellState();
}

class _PropertyListShellState extends State<PropertyListShell> {
  int _currentTab = 0;

  void _onTabTapped(int value) {
    if (_currentTab == value) return;
    setState(() => _currentTab = value);
  }

  static const int _createTabIndex = 4;

  void _openCreateTab() {
    if (_currentTab == _createTabIndex) return;
    setState(() => _currentTab = _createTabIndex);
  }

  @override
  Widget build(BuildContext context) {
    final tabs = [
      PropertyListTab(onAddTapped: _openCreateTab),
      const VehicleListScreen(showAppBar: false),
      const MapScreen(showAppBar: false),
      const QuickValuationScreen(showAppBar: false),
      const PropertyCreateScreen(showAppBar: false),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConstants.appName),
        actions: [
          BlocListener<SyncBloc, SyncState>(
            listener: (context, syncState) {
              if (syncState.status == SyncStatus.synced) {
                context.read<PropertyBloc>().add(LoadProperties());
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Sync complete')),
                );
              } else if (syncState.status == SyncStatus.failed &&
                  syncState.message != null) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Sync failed: ${syncState.message}')),
                );
              }
            },
            child: BlocBuilder<SyncBloc, SyncState>(
              buildWhen: (p, c) => p.status != c.status,
              builder: (context, syncState) {
                return IconButton(
                  icon: syncState.status == SyncStatus.syncing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.sync),
                  onPressed: syncState.status == SyncStatus.syncing ||
                          !syncState.isOnline
                      ? null
                      : () => context.read<SyncBloc>().add(SyncTriggered()),
                );
              },
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () =>
                context.read<AuthBloc>().add(AuthLogoutRequested()),
          ),
        ],
      ),
      body: BlocBuilder<SyncBloc, SyncState>(
        builder: (context, syncState) {
          return Column(
            children: [
              AppSyncBanner(syncState: syncState),
              Expanded(
                child: IndexedStack(
                  index: _currentTab,
                  children: tabs,
                ),
              ),
            ],
          );
        },
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTab,
        onTap: _onTabTapped,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Properties'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car_outlined),
            label: 'Vehicles',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.map_outlined), label: 'Map'),
          BottomNavigationBarItem(
            icon: Icon(Icons.calculate_outlined),
            label: 'Valuation',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_circle_outline),
            label: 'New',
          ),
        ],
      ),
    );
  }
}

class PropertyListTab extends StatelessWidget {
  final VoidCallback onAddTapped;

  const PropertyListTab({
    super.key,
    required this.onAddTapped,
  });

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<SyncBloc, SyncState>(
      builder: (context, syncState) {
        return BlocBuilder<PropertyBloc, PropertyState>(
          builder: (context, state) {
            if (state.status == PropertyStatus.loading &&
                state.properties.isEmpty) {
              return const AppLoadingState(message: 'Loading properties...');
            }

            if (state.status == PropertyStatus.error &&
                state.properties.isEmpty) {
              return AppEmptyState(
                icon: Icons.cloud_off,
                title: 'Could not load properties',
                message: syncState.isOnline
                    ? (state.message ??
                        'Please retry to load your property list.')
                    : 'No network. Showing only locally stored properties.',
                actionLabel:
                    syncState.isOnline ? 'Retry' : 'Check offline mode',
                onAction: syncState.isOnline
                    ? () => context.read<PropertyBloc>().add(LoadProperties())
                    : () =>
                        context.read<AuthBloc>().add(AuthOfflineRequested()),
              );
            }

            if (state.properties.isEmpty) {
              final offlineCopy = syncState.isOnline
                  ? 'Use New to add your first property.'
                  : 'You are offline. Add a property now and sync it later.';
              return AppEmptyState(
                icon: Icons.add_home_work,
                title: syncState.isOnline
                    ? 'No properties yet'
                    : 'No local properties yet',
                message: offlineCopy,
                actionLabel: 'Add property',
                onAction: onAddTapped,
              );
            }

            final isSyncing = syncState.status == SyncStatus.syncing;
            final isSyncFailed = syncState.status == SyncStatus.failed;

            return RefreshIndicator(
              onRefresh: () async {
                if (!syncState.isOnline || isSyncing) {
                  return;
                }

                context.read<PropertyBloc>().add(LoadProperties());
              },
              child: Column(
                children: [
                  if (isSyncFailed && syncState.message != null)
                    Padding(
                      padding: const EdgeInsets.fromLTRB(
                        AppSpacing.md,
                        AppSpacing.sm,
                        AppSpacing.md,
                        0,
                      ),
                      child: AppEmptyState(
                        icon: Icons.sync_problem,
                        title: 'Sync blocked',
                        message: syncState.message!,
                        actionLabel: 'Retry sync',
                        onAction: () =>
                            context.read<SyncBloc>().add(SyncTriggered()),
                      ),
                    ),
                  if (isSyncing)
                    const Padding(
                      padding: EdgeInsets.fromLTRB(
                        AppSpacing.md,
                        AppSpacing.sm,
                        AppSpacing.md,
                        0,
                      ),
                      child: LinearProgressIndicator(),
                    ),
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(
                        vertical: AppSpacing.sm,
                        horizontal: AppSpacing.md,
                      ),
                      itemCount: state.properties.length,
                      itemBuilder: (context, index) {
                        final property = state.properties[index];
                        return PropertyCard(
                          property: property,
                          onTap: () => Navigator.of(context).pushNamed(
                            PropertyDetailScreen.routeName,
                            arguments: PropertyDetailScreenArgs(property),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
