import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/auth/auth_bloc.dart';
import '../bloc/auth/auth_event.dart';
import '../bloc/auth/auth_state.dart';
import '../bloc/property/property_event.dart';
import '../bloc/sync/sync_bloc.dart';
import '../bloc/sync/sync_event.dart';
import '../bloc/vehicle/vehicle_event.dart';
import 'theme/app_theme.dart';
import 'bloc_providers.dart';
import 'screens/login_screen.dart';
import 'screens/property_list_screen.dart';
import 'screens/property_detail_screen.dart';
import 'screens/vehicle_detail_screen.dart';

class ValuAdisApp extends StatelessWidget {
  const ValuAdisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ValuAdis',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.build(),
      routes: {
        PropertyDetailScreen.routeName: (context) {
          final args = ModalRoute.of(context)?.settings.arguments;
          if (args is PropertyDetailScreenArgs) {
            return MultiBlocProvider(
              providers: [
                BlocProvider.value(value: blocProviders.propertyBloc),
                BlocProvider.value(value: blocProviders.valuationBloc),
                BlocProvider.value(value: blocProviders.syncBloc),
              ],
              child: PropertyDetailScreen(property: args.property),
            );
          }
          return const Scaffold(
            body: Center(child: Text('Missing property detail arguments')),
          );
        },
        VehicleDetailScreen.routeName: (context) {
          final args = ModalRoute.of(context)?.settings.arguments;
          if (args is VehicleDetailScreenArgs) {
            return BlocProvider.value(
              value: blocProviders.vehicleBloc,
              child: VehicleDetailScreen(vehicle: args.vehicle),
            );
          }
          return const Scaffold(
            body: Center(child: Text('Missing vehicle detail arguments')),
          );
        },
      },
      home: Builder(
        builder: (context) {
          final authBloc = blocProviders.authBloc..add(AuthCheckRequested());
          blocProviders.apiClient.setUnauthorizedHandler(
            (message) => authBloc.add(AuthSessionExpired(message: message)),
          );

          return BlocProvider.value(
            value: authBloc,
            child: const _AppRouter(),
          );
        },
      ),
    );
  }
}

class _AppRouter extends StatelessWidget {
  const _AppRouter();

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      buildWhen: (prev, curr) => prev.status != curr.status,
      builder: (context, state) {
        switch (state.status) {
          case AuthStatus.authenticated:
            return MultiBlocProvider(
              providers: [
                BlocProvider.value(
                  value: blocProviders.propertyBloc..add(LoadProperties()),
                ),
                BlocProvider.value(
                  value: blocProviders.valuationBloc,
                ),
                BlocProvider.value(value: blocProviders.syncBloc),
                BlocProvider.value(
                  value: blocProviders.vehicleBloc..add(LoadVehicles()),
                ),
                BlocProvider.value(value: blocProviders.quickValuationBloc),
              ],
              child: const _ForegroundSyncGate(
                child: PropertyListScreen(),
              ),
            );
          case AuthStatus.loading:
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          default:
            return const LoginScreen();
        }
      },
    );
  }
}

class _ForegroundSyncGate extends StatefulWidget {
  final Widget child;

  const _ForegroundSyncGate({
    required this.child,
  });

  @override
  State<_ForegroundSyncGate> createState() => _ForegroundSyncGateState();
}

class _ForegroundSyncGateState extends State<_ForegroundSyncGate>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!mounted || state != AppLifecycleState.resumed) return;
    context.read<SyncBloc>().add(SyncTriggered());
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
