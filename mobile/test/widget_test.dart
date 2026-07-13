import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';

import 'package:valuadis/bloc/auth/auth_bloc.dart';
import 'package:valuadis/bloc/auth/auth_event.dart';
import 'package:valuadis/bloc/auth/auth_state.dart';
import 'package:valuadis/bloc/property/property_bloc.dart';
import 'package:valuadis/bloc/property/property_event.dart';
import 'package:valuadis/bloc/property/property_state.dart';
import 'package:valuadis/bloc/sync/sync_bloc.dart';
import 'package:valuadis/bloc/sync/sync_event.dart';
import 'package:valuadis/bloc/sync/sync_state.dart';
import 'package:valuadis/bloc/quick_valuation/quick_valuation_bloc.dart';
import 'package:valuadis/bloc/valuation/valuation_bloc.dart';
import 'package:valuadis/bloc/valuation/valuation_event.dart';
import 'package:valuadis/bloc/vehicle/vehicle_bloc.dart';
import 'package:valuadis/data/models/valuation.dart';
import 'package:valuadis/data/models/photo.dart';
import 'package:valuadis/data/models/property.dart';
import 'package:valuadis/data/models/vehicle.dart';
import 'package:valuadis/data/repositories/auth_repository.dart';
import 'package:valuadis/data/repositories/property_repository.dart';
import 'package:valuadis/data/repositories/photo_repository.dart';
import 'package:valuadis/data/repositories/quick_valuation_repository.dart';
import 'package:valuadis/data/repositories/valuation_repository.dart';
import 'package:valuadis/data/repositories/vehicle_repository.dart';
import 'package:valuadis/data/datasources/remote/api_client.dart';
import 'package:valuadis/presentation/bloc_providers.dart';
import 'package:valuadis/presentation/screens/login_screen.dart';
import 'package:valuadis/presentation/screens/property_list_screen.dart';
import 'package:valuadis/presentation/screens/map_screen.dart';
import 'package:valuadis/presentation/screens/property_detail_screen.dart';
import 'package:valuadis/presentation/widgets/property_card.dart';
import 'package:valuadis/presentation/widgets/shared_ui.dart';
import 'package:valuadis/presentation/theme/app_theme.dart';

const _connectivityMethodChannel = MethodChannel(
  'dev.fluttercommunity.plus/connectivity',
);

Future<void> _mockConnectivityCheck(String value) async {
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .setMockMethodCallHandler(
    _connectivityMethodChannel,
    (MethodCall methodCall) async {
      if (methodCall.method == 'check') {
        return value;
      }
      return null;
    },
  );
}

class _TestAuthRepository extends AuthRepository {
  bool loginOfflineCalled = false;
  bool loginAttempted = false;
  bool _isLoggedIn = false;
  final bool loginReturn;

  _TestAuthRepository({
    this.loginReturn = false,
    bool loggedIn = false,
  }) {
    _isLoggedIn = loggedIn;
  }

  @override
  bool get isLoggedIn => _isLoggedIn;

  @override
  Future<bool> login(String email, String password) async {
    loginAttempted = true;
    if (loginReturn) {
      _isLoggedIn = true;
    }
    return loginReturn;
  }

  @override
  Future<void> logout() async {}

  @override
  Future<void> loginOffline() async {
    loginOfflineCalled = true;
    _isLoggedIn = true;
  }
}

class _TrackingAuthRepository extends _TestAuthRepository {
  _TrackingAuthRepository({
    super.loginReturn = false,
  });

  @override
  Future<bool> login(String email, String password) async =>
      await super.login(email, password).then((_) async {
        await Future<void>.delayed(const Duration(milliseconds: 50));
        return loginReturn;
      });

  @override
  Future<void> loginOffline() async {
    loginOfflineCalled = true;
    await Future<void>.delayed(const Duration(milliseconds: 50));
  }
}

class _SlowAuthRepository extends _TestAuthRepository {
  @override
  Future<bool> login(String email, String password) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return loginReturn;
  }
}

class _FlowPropertyRepository extends PropertyRepository {
  _FlowPropertyRepository([List<Property>? seed])
      : _properties = List<Property>.from(seed ?? []);

  final List<Property> _properties;
  final Map<int, int> _retryCounts = {};
  int loadCount = 0;
  int createCount = 0;
  int syncUpdateCount = 0;

  int _nextId = 1;

  @override
  Future<List<Property>> getAllProperties() async {
    loadCount += 1;
    return List<Property>.from(_properties);
  }

  @override
  Future<List<Property>> getPendingSync() async {
    return _properties
        .where((property) => property.syncStatus != 'synced')
        .toList();
  }

  @override
  Future<Property?> getById(int id) async {
    final index = _properties.indexWhere((property) => property.id == id);
    if (index < 0) return null;
    return _properties[index];
  }

  @override
  Future<int> getRetryCount(int id) async {
    return _retryCounts[id] ?? 0;
  }

  @override
  Future<int> createProperty(Property property) async {
    createCount += 1;
    final id = property.id ?? _nextId++;
    final created = property.copyWith(
      id: id,
      syncStatus: property.syncStatus,
    );
    _properties.add(created);
    if (id >= _nextId) {
      _nextId = id + 1;
    }
    return id;
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    syncUpdateCount += 1;
    final index = _properties.indexWhere((property) => property.id == id);
    if (index < 0) return 0;
    _properties[index] = _properties[index].copyWith(syncStatus: status);
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    _retryCounts[id] = retryCount + 1;
    return 1;
  }

  @override
  Future<int> updateProperty(Property property) async {
    final index = _properties.indexWhere((item) => item.id == property.id);
    if (index == -1) return 0;
    _properties[index] = property;
    return 1;
  }

  @override
  Future<int> updateServerId(int id, int serverId) async {
    final index = _properties.indexWhere((item) => item.id == id);
    if (index == -1) return 0;
    _properties[index] = _properties[index].copyWith(serverId: serverId);
    return 1;
  }

  List<Property> snapshot() => List<Property>.from(_properties);
}

class _FlowValuationRepository extends ValuationRepository {
  _FlowValuationRepository([List<Valuation>? seed])
      : _valuations = List<Valuation>.from(seed ?? []);

  final List<Valuation> _valuations;
  int loadCount = 0;
  int syncUpdateCount = 0;
  int createCount = 0;
  final Map<int, int> _retryCounts = {};

  @override
  Future<List<Valuation>> getValuationsByPropertyId(int propertyId) async {
    loadCount += 1;
    return _valuations
        .where((valuation) => valuation.propertyId == propertyId)
        .toList();
  }

  @override
  Future<int> createValuation(Valuation valuation) async {
    createCount += 1;
    final id = valuation.id ?? _valuations.length + 1;
    _valuations.add(valuation.copyWith(id: id));
    return id;
  }

  @override
  Future<List<Valuation>> getPendingSync() async {
    return _valuations
        .where((valuation) => valuation.syncStatus != 'synced')
        .toList();
  }

  @override
  Future<int> getRetryCount(int id) async {
    return _retryCounts[id] ?? 0;
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    syncUpdateCount += 1;
    final index = _valuations.indexWhere((valuation) => valuation.id == id);
    if (index == -1) return 0;
    _valuations[index] = _valuations[index].copyWith(syncStatus: status);
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    _retryCounts[id] = retryCount + 1;
    return 1;
  }

  List<Valuation> snapshot() => List<Valuation>.from(_valuations);
}

class _FlowApiClient extends ApiClient {
  _FlowApiClient(this.handlePost);

  final Future<Response<dynamic>> Function(String path, dynamic data)
      handlePost;

  @override
  Future<Response> post(String path, {dynamic data}) {
    return handlePost(path, data);
  }

  /// Pull requests return an empty server payload so the two-way sync stays
  /// network-free; these flow tests only exercise the push path.
  @override
  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) {
    return Future.value(
      Response<dynamic>(
        requestOptions: RequestOptions(path: path),
        statusCode: 200,
        data: {'success': true, 'data': <dynamic>[]},
      ),
    );
  }
}

Widget _buildFlowApp({
  required AuthRepository authRepository,
  required PropertyRepository propertyRepository,
  required ValuationRepository valuationRepository,
  required SyncBloc syncBloc,
}) {
  final authBloc = AuthBloc(authRepository)..add(AuthCheckRequested());
  final propertyBloc = PropertyBloc(propertyRepository);
  final valuationBloc = ValuationBloc(valuationRepository);

  return MaterialApp(
    onGenerateRoute: (settings) {
      if (settings.name == PropertyDetailScreen.routeName) {
        final args = settings.arguments;
        if (args is PropertyDetailScreenArgs) {
          return MaterialPageRoute<void>(
            builder: (_) => MultiBlocProvider(
              providers: [
                BlocProvider.value(value: propertyBloc),
                BlocProvider.value(value: valuationBloc),
                BlocProvider.value(value: syncBloc),
              ],
              child: PropertyDetailScreen(property: args.property),
            ),
          );
        }
      }
      return MaterialPageRoute<void>(
        builder: (_) => const Scaffold(
          body: Center(child: Text('Missing property detail arguments')),
        ),
      );
    },
    home: MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (_) => authBloc,
        ),
        BlocProvider<PropertyBloc>(
          create: (_) => propertyBloc,
        ),
        BlocProvider<ValuationBloc>(
          create: (_) => valuationBloc,
        ),
        BlocProvider<SyncBloc>(create: (_) => syncBloc),
        BlocProvider<VehicleBloc>(create: (_) => _testVehicleBloc()),
        BlocProvider<QuickValuationBloc>(
          create: (_) => _testQuickValuationBloc(),
        ),
      ],
      child: Builder(
        builder: (context) {
          return BlocBuilder<AuthBloc, AuthState>(
            buildWhen: (prev, curr) => prev.status != curr.status,
            builder: (context, state) {
              if (state.status == AuthStatus.authenticated) {
                if (context.read<PropertyBloc>().state.status ==
                    PropertyStatus.initial) {
                  context.read<PropertyBloc>().add(LoadProperties());
                }
                return const PropertyListScreen();
              }
              return const LoginScreen();
            },
          );
        },
      ),
    ),
  );
}

Widget _buildPropertyDetailHarness({
  required Property property,
  required PropertyRepository propertyRepository,
  required ValuationRepository valuationRepository,
  required SyncBloc syncBloc,
}) {
  return MaterialApp(
    home: MultiBlocProvider(
      providers: [
        BlocProvider<PropertyBloc>(
          create: (_) => PropertyBloc(propertyRepository),
        ),
        BlocProvider<ValuationBloc>(
          create: (_) => ValuationBloc(valuationRepository),
        ),
        BlocProvider<SyncBloc>(create: (_) => syncBloc),
      ],
      child: PropertyDetailScreen(property: property),
    ),
  );
}

class _StaticPropertyRepository extends PropertyRepository {
  final Future<List<Property>> Function() _properties;

  _StaticPropertyRepository(this._properties);

  @override
  Future<List<Property>> getAllProperties() {
    return _properties();
  }

  @override
  Future<List<Property>> getPendingSync() async => const [];
}

class _MutablePropertyRepository extends PropertyRepository {
  _MutablePropertyRepository(this._properties);

  final List<Property> _properties;
  int updateCalls = 0;

  @override
  Future<List<Property>> getAllProperties() async {
    return List<Property>.from(_properties);
  }

  @override
  Future<List<Property>> getPendingSync() async => const [];

  @override
  Future<int> createProperty(Property property) async {
    _properties.add(property);
    return 1;
  }

  @override
  Future<int> updateProperty(Property property) async {
    updateCalls += 1;
    final index = _properties.indexWhere((item) => item.id == property.id);
    if (index == -1) return 0;
    _properties[index] = property;
    return 1;
  }

  List<Property> snapshot() => List<Property>.from(_properties);
}

Widget _buildLoginScreen(AuthRepository repository) {
  return MaterialApp(
    home: BlocProvider<AuthBloc>(
      create: (_) => AuthBloc(repository)..add(AuthCheckRequested()),
      child: const LoginScreen(),
    ),
  );
}

Widget _buildPropertyList(
  PropertyBloc bloc, {
  SyncBloc? syncBloc,
  ValuationBloc? valuationBloc,
}) {
  final effectiveSyncBloc = syncBloc ?? _TestSyncBloc();
  final effectiveValuationBloc = valuationBloc ?? _TestValuationBloc();

  return MultiBlocProvider(
    providers: [
      BlocProvider<PropertyBloc>(create: (_) => bloc),
      BlocProvider<SyncBloc>(create: (_) => effectiveSyncBloc),
      BlocProvider<ValuationBloc>(create: (_) => effectiveValuationBloc),
    ],
    child: MaterialApp(
      onGenerateRoute: (settings) {
        if (settings.name == PropertyDetailScreen.routeName) {
          final args = settings.arguments;
          if (args is PropertyDetailScreenArgs) {
            return MaterialPageRoute<void>(
              builder: (_) => MultiBlocProvider(
                providers: [
                  BlocProvider.value(value: bloc),
                  BlocProvider.value(value: effectiveSyncBloc),
                  BlocProvider.value(value: effectiveValuationBloc),
                ],
                child: PropertyDetailScreen(property: args.property),
              ),
            );
          }
        }
        return MaterialPageRoute<void>(
          builder: (_) => const Scaffold(
            body: Center(child: Text('Missing property detail arguments')),
          ),
        );
      },
      home: Scaffold(
        body: PropertyListTab(onAddTapped: () {}),
      ),
    ),
  );
}

class _TestSyncPropertyRepository extends PropertyRepository {
  @override
  Future<List<Property>> getPendingSync() async => const [];

  @override
  Future<List<Property>> getAllProperties() async => const [];
}

class _TestValuationRepository extends ValuationRepository {
  _TestValuationRepository([List<Valuation>? initial])
      : _valuations = initial ?? [];

  final List<Valuation> _valuations;

  @override
  Future<int> createValuation(Valuation valuation) async {
    _valuations.add(valuation);
    return 1;
  }

  @override
  Future<List<Valuation>> getValuationsByPropertyId(int propertyId) async {
    return _valuations
        .where((valuation) => valuation.propertyId == propertyId)
        .toList(growable: false);
  }

  @override
  Future<List<Valuation>> getPendingSync() async {
    return _valuations
        .where((valuation) => valuation.syncStatus == 'pending')
        .toList(growable: false);
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    final index = _valuations.indexWhere((valuation) => valuation.id == id);
    if (index == -1) return 0;
    _valuations[index] = _valuations[index].copyWith(syncStatus: status);
    return 1;
  }

  List<Valuation> snapshot() => List<Valuation>.from(_valuations);
}

class _TestPhotoRepository extends PhotoRepository {
  _TestPhotoRepository([List<Photo>? seed])
      : _photos = List<Photo>.from(seed ?? []);

  final List<Photo> _photos;

  @override
  Future<int> addPhoto(Photo photo) async {
    _photos.add(photo);
    return _photos.length;
  }

  @override
  Future<List<Photo>> getPhotosForProperty(int propertyId) async =>
      _photos.where((photo) => photo.propertyId == propertyId).toList();
}

class _TestValuationBloc extends ValuationBloc {
  _TestValuationBloc([_TestValuationRepository? repository])
      : repository = repository ?? _TestValuationRepository(),
        super(repository ?? _TestValuationRepository());

  final _TestValuationRepository repository;
}

class _TestSyncValuationRepository extends ValuationRepository {}

class _TestApiClient extends ApiClient {}

class _TestVehicleRepository extends VehicleRepository {
  _TestVehicleRepository() : super(_TestApiClient());

  @override
  Future<List<Vehicle>> getVehicles() async => const [];
}

class _TestQuickValuationRepository extends QuickValuationRepository {
  _TestQuickValuationRepository() : super(_TestApiClient());
}

VehicleBloc _testVehicleBloc() => VehicleBloc(_TestVehicleRepository());

QuickValuationBloc _testQuickValuationBloc() =>
    QuickValuationBloc(_TestQuickValuationRepository());

class _TestSyncBloc extends SyncBloc {
  _TestSyncBloc()
      : super(
          _TestSyncPropertyRepository(),
          _TestSyncValuationRepository(),
          _TestApiClient(),
        );

  void setOffline() {
    emit(const SyncState(isOnline: false));
  }

  void setSyncing() {
    emit(const SyncState(status: SyncStatus.syncing, isOnline: true));
  }

  void setSynced() {
    emit(const SyncState(status: SyncStatus.synced, isOnline: true));
  }
}

Widget _buildPropertyListScreen({required SyncBloc syncBloc}) {
  return MaterialApp(
    home: MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (_) =>
              AuthBloc(_TestAuthRepository())..add(AuthCheckRequested()),
        ),
        BlocProvider<PropertyBloc>(
          create: (_) => PropertyBloc(
            _StaticPropertyRepository(() async => const <Property>[]),
          ),
        ),
        BlocProvider<SyncBloc>(
          create: (_) => syncBloc,
        ),
        BlocProvider<ValuationBloc>(
          create: (_) => _TestValuationBloc(),
        ),
        BlocProvider<VehicleBloc>(
          create: (_) => _testVehicleBloc(),
        ),
        BlocProvider<QuickValuationBloc>(
          create: (_) => _testQuickValuationBloc(),
        ),
      ],
      child: const PropertyListScreen(),
    ),
  );
}

Widget _buildSyncBanner(SyncState syncState) {
  return MaterialApp(
    home: Scaffold(
      body: AppSyncBanner(syncState: syncState),
    ),
  );
}

Property _sampleProperty() => const Property(
      id: 1,
      address: 'Addis Ababa, Bole',
      propertyType: 'Apartment',
      areaSqm: 120,
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
    );

void main() {
  testWidgets('Login screen renders key controls', (WidgetTester tester) async {
    await tester.pumpWidget(_buildLoginScreen(_TestAuthRepository()));

    expect(find.text('Welcome to ValuAdis'), findsOneWidget);
    expect(find.byIcon(Icons.email_outlined), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });

  testWidgets('Login screen shows loading and error states',
      (WidgetTester tester) async {
    await tester.pumpWidget(_buildLoginScreen(_SlowAuthRepository()));

    await tester.enterText(
        find.byType(TextFormField).first, 'test@example.com');
    await tester.enterText(find.byType(TextFormField).last, 'wrong-password');
    await tester.tap(find.text('Sign in'));
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle();
    expect(find.text('Login failed. Check credentials or try offline mode.'),
        findsOneWidget);
  });

  testWidgets('Login screen offline fallback is actionable and clears errors',
      (WidgetTester tester) async {
    final repository = _TrackingAuthRepository();
    await tester.pumpWidget(_buildLoginScreen(repository));

    await tester.enterText(
        find.byType(TextFormField).first, 'test@example.com');
    await tester.enterText(find.byType(TextFormField).last, 'wrong-password');
    await tester.tap(find.text('Sign in'));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(repository.loginAttempted, isTrue);
    expect(find.text('Login failed. Check credentials or try offline mode.'),
        findsOneWidget);

    await tester.tap(find.text('Continue offline'));
    await tester.pumpAndSettle();

    expect(repository.loginOfflineCalled, isTrue);
    expect(find.text('Login failed. Check credentials or try offline mode.'),
        findsNothing);
    expect(find.text('Continue offline'), findsOneWidget);
  });

  testWidgets('Theme constants are centralized and applied by the app theme',
      (WidgetTester tester) async {
    final theme = AppTheme.build();

    expect(theme.scaffoldBackgroundColor, AppColors.background);
    expect(theme.cardTheme.color, AppColors.surface);
    expect(theme.textTheme.titleMedium?.fontFamily, AppTypo.fontFamily);
    expect(theme.colorScheme.primary, AppColors.primary);
    expect(theme.colorScheme.error, AppColors.error);
    expect(theme.textTheme.titleLarge?.fontWeight, FontWeight.w600);

    await tester.pumpWidget(
      MaterialApp(
        theme: theme,
        home: const Scaffold(body: SizedBox.shrink()),
      ),
    );
    expect(find.byType(Scaffold), findsOneWidget);
  });

  testWidgets(
      'Reusable shared UI components are consumed across multiple screens',
      (WidgetTester tester) async {
    await tester.pumpWidget(_buildLoginScreen(_TestAuthRepository()));
    expect(find.byType(AppCard), findsOneWidget);
    expect(find.byType(AppSectionHeader), findsAtLeast(1));

    final syncBloc = _TestSyncBloc();
    final propertyBloc = PropertyBloc(
      _StaticPropertyRepository(
        () async => const <Property>[
          Property(
            id: 1,
            address: 'Addis Ababa, Bole',
            propertyType: 'Apartment',
            areaSqm: 120,
            createdAt: '2026-01-01T00:00:00Z',
            updatedAt: '2026-01-01T00:00:00Z',
            syncStatus: 'synced',
          ),
        ],
      ),
    );

    await tester.pumpWidget(
      _buildPropertyList(
        propertyBloc,
        syncBloc: syncBloc,
      ),
    );
    propertyBloc.add(LoadProperties());
    await tester.pump();
    expect(find.byType(AppCard), findsAtLeast(1));
    expect(find.byType(AppStatusChip), findsAtLeast(1));
    expect(find.byType(AppEmptyState), findsNothing);

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: MapScreen(showAppBar: false),
        ),
      ),
    );
    expect(find.byType(AppEmptyState), findsAtLeast(1));

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MultiBlocProvider(
            providers: [
              BlocProvider<PropertyBloc>(
                create: (_) => PropertyBloc(
                    _StaticPropertyRepository(() async => const [])),
              ),
              BlocProvider<SyncBloc>(create: (_) => _TestSyncBloc()),
              BlocProvider<ValuationBloc>(create: (_) => _TestValuationBloc()),
            ],
            child: PropertyDetailScreen(
              property: _sampleProperty().copyWith(syncStatus: 'synced'),
            ),
          ),
        ),
      ),
    );
    expect(find.byType(AppStatusChip), findsOneWidget);
    expect(find.byType(AppCard), findsOneWidget);
    expect(find.byType(AppSectionHeader), findsAtLeast(1));
  });

  testWidgets('Property list shows empty state', (WidgetTester tester) async {
    await tester.pumpWidget(
      _buildPropertyList(
        PropertyBloc(
          _StaticPropertyRepository(() async => const <Property>[]),
        ),
      ),
    );

    expect(find.text('No properties yet'), findsOneWidget);
    expect(find.text('Use New to add your first property.'), findsOneWidget);
    expect(find.text('Add property'), findsOneWidget);
  });

  testWidgets('Property list shows loading state', (WidgetTester tester) async {
    final bloc = PropertyBloc(
      _StaticPropertyRepository(() async {
        await Future<void>.delayed(const Duration(milliseconds: 250));
        return const <Property>[];
      }),
    );
    await tester.pumpWidget(_buildPropertyList(bloc));

    bloc.add(LoadProperties());
    await tester.pump();
    expect(find.text('Loading properties...'), findsOneWidget);

    await tester.pumpAndSettle();
    expect(find.text('No properties yet'), findsOneWidget);
  });

  testWidgets('Property list shows error state', (WidgetTester tester) async {
    final bloc = PropertyBloc(
      _StaticPropertyRepository(
        () async => throw Exception('db unavailable'),
      ),
    );
    await tester.pumpWidget(_buildPropertyList(bloc));

    bloc.add(LoadProperties());
    await tester.pumpAndSettle();
    expect(find.text('Could not load properties'), findsOneWidget);
    expect(find.textContaining('db unavailable'), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
  });

  testWidgets('Property list shows offline-friendly empty state',
      (WidgetTester tester) async {
    final syncBloc = _TestSyncBloc();
    syncBloc.setOffline();
    await tester.pumpWidget(
      _buildPropertyList(
        PropertyBloc(
          _StaticPropertyRepository(() async => const <Property>[]),
        ),
        syncBloc: syncBloc,
      ),
    );

    expect(find.text('No local properties yet'), findsOneWidget);
    expect(find.text('You are offline. Add a property now and sync it later.'),
        findsOneWidget);
    expect(find.text('Add property'), findsOneWidget);
  });

  testWidgets('Property card callback is triggered on tap',
      (WidgetTester tester) async {
    var tapped = false;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: PropertyCard(
            property: _sampleProperty(),
            onTap: () {
              tapped = true;
            },
          ),
        ),
      ),
    );

    await tester.tap(find.byType(ListTile));
    expect(tapped, isTrue);
  });

  testWidgets('Property card in list opens detail screen',
      (WidgetTester tester) async {
    final syncBloc = _TestSyncBloc();
    final propertyBloc = PropertyBloc(
      _StaticPropertyRepository(() async => <Property>[_sampleProperty()]),
    );
    await tester
        .pumpWidget(_buildPropertyList(propertyBloc, syncBloc: syncBloc));
    propertyBloc.add(LoadProperties());

    await tester.pumpAndSettle();
    await tester.tap(find.text('Addis Ababa, Bole'));
    await tester.pumpAndSettle();
    expect(find.text('Property detail'), findsOneWidget);

    expect(find.text('Addis Ababa, Bole'), findsOneWidget);
    expect(find.text('Apartment'), findsOneWidget);
    expect(find.text('Property detail'), findsOneWidget);
    expect(find.text('Boundary not set'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.textContaining('Created '),
      150,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.textContaining('Created '), findsOneWidget);
  });

  testWidgets('Property edit updates list and repository',
      (WidgetTester tester) async {
    final repository = _MutablePropertyRepository(
      <Property>[_sampleProperty()],
    );
    final propertyBloc = PropertyBloc(repository);
    await tester.pumpWidget(_buildPropertyList(propertyBloc));
    propertyBloc.add(LoadProperties());

    await tester.pumpAndSettle();
    await tester.tap(find.text('Addis Ababa, Bole'));
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Edit property'));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('edit-address-field')), findsOneWidget);
    await tester.enterText(
      find.byKey(const Key('edit-address-field')),
      'Bole Plaza',
    );
    await tester.tap(find.text('Save'));
    await tester.pump();
    await tester.pumpAndSettle();

    propertyBloc.add(LoadProperties());
    await tester.pumpAndSettle();

    expect(repository.updateCalls, isPositive);
    expect(repository.snapshot().first.address, equals('Bole Plaza'));
    expect(find.text('Bole Plaza'), findsOneWidget);
  });

  testWidgets('Property detail can add a valuation and show latest summary',
      (WidgetTester tester) async {
    final propertyBloc = PropertyBloc(
      _StaticPropertyRepository(() async => <Property>[_sampleProperty()]),
    );
    final valuationRepository = _TestValuationRepository();
    final valuationBloc = _TestValuationBloc(valuationRepository);

    await tester.pumpWidget(
      _buildPropertyList(
        propertyBloc,
        valuationBloc: valuationBloc,
      ),
    );
    propertyBloc.add(LoadProperties());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Addis Ababa, Bole'));
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Add valuation'));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('valuation-market-field')), findsOneWidget);
    await tester.enterText(
      find.byKey(const Key('valuation-market-field')),
      '125000',
    );
    await tester.enterText(
      find.byKey(const Key('valuation-taxable-field')),
      '118000',
    );
    await tester.tap(find.text('Save'));
    await tester.pump(const Duration(milliseconds: 200));
    await tester.pumpAndSettle();

    expect(valuationBloc.state.valuations, isNotEmpty);
    expect(valuationRepository.snapshot().length, equals(1));
    await tester.drag(find.byType(ListView).first, const Offset(0, -300));
    await tester.pumpAndSettle();
    expect(find.textContaining('Market:'), findsOneWidget);
    expect(
      find.textContaining('Taxable:'),
      findsOneWidget,
    );
  });

  testWidgets('Property detail shows photo empty state',
      (WidgetTester tester) async {
    final propertyBloc = PropertyBloc(
      _StaticPropertyRepository(() async => <Property>[_sampleProperty()]),
    );

    await tester.pumpWidget(_buildPropertyList(propertyBloc));
    propertyBloc.add(LoadProperties());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Addis Ababa, Bole'));
    await tester.pumpAndSettle();

    expect(find.byTooltip('Attach photo'), findsOneWidget);
    expect(find.text('No photos yet'), findsOneWidget);
  });

  testWidgets('Sync banner renders offline, syncing, and synced labels',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      _buildSyncBanner(const SyncState(isOnline: false)),
    );
    expect(find.text('Offline. Changes saved locally.'), findsOneWidget);

    await tester.pumpWidget(
      _buildSyncBanner(
        const SyncState(status: SyncStatus.syncing, isOnline: true),
      ),
    );
    expect(find.text('Syncing pending data'), findsOneWidget);

    await tester.pumpWidget(
      _buildSyncBanner(
        const SyncState(status: SyncStatus.synced, isOnline: true),
      ),
    );
    expect(find.text('Sync complete'), findsOneWidget);
  });

  testWidgets('Property list shell shows sync offline banner',
      (WidgetTester tester) async {
    final syncBloc = _TestSyncBloc();
    await tester.pumpWidget(_buildPropertyListScreen(syncBloc: syncBloc));
    expect(find.byType(AppBar), findsOneWidget);
    syncBloc.setOffline();
    await tester.pump();
    expect(find.text('Offline. Changes saved locally.'), findsOneWidget);
  });

  testWidgets('Property list shell updates banner on sync status transitions',
      (WidgetTester tester) async {
    final syncBloc = _TestSyncBloc();
    await tester.pumpWidget(_buildPropertyListScreen(syncBloc: syncBloc));

    expect(find.text('Offline. Changes saved locally.'), findsNothing);
    expect(find.text('Syncing pending data'), findsNothing);
    expect(find.text('Sync complete'), findsNothing);

    syncBloc.setSyncing();
    await tester.pump();
    expect(find.text('Syncing pending data'), findsOneWidget);

    syncBloc.setOffline();
    await tester.pump();
    expect(find.text('Offline. Changes saved locally.'), findsOneWidget);
    expect(find.text('Syncing pending data'), findsNothing);

    syncBloc.setSynced();
    await tester.pump();
    expect(find.text('Sync complete'), findsAtLeast(1));
  });

  testWidgets(
      '13.1 Login demo flow opens list and refresh path can be triggered',
      (WidgetTester tester) async {
    final propertyRepository = _FlowPropertyRepository([_sampleProperty()]);
    final valuationRepository = _FlowValuationRepository();
    final authRepository = _TrackingAuthRepository(loginReturn: false);
    final syncBloc = _TestSyncBloc();

    await tester.pumpWidget(
      _buildFlowApp(
        authRepository: authRepository,
        propertyRepository: propertyRepository,
        valuationRepository: valuationRepository,
        syncBloc: syncBloc,
      ),
    );

    expect(find.text('Welcome to ValuAdis'), findsOneWidget);
    await tester.tap(find.text('Continue offline'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.byType(PropertyListTab), findsOneWidget);
    final propertyBloc =
        tester.element(find.byType(PropertyListTab)).read<PropertyBloc>();
    final loadCountBefore = propertyRepository.loadCount;
    propertyBloc.add(LoadProperties());
    await tester.pump(const Duration(milliseconds: 100));
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.byType(PropertyCard), findsOneWidget);
    expect(propertyRepository.loadCount, greaterThan(loadCountBefore));
  });

    testWidgets('13.2 Create property with boundary and sync it',
      (WidgetTester tester) async {
    final propertyRepository = _FlowPropertyRepository();
    final valuationRepository = _FlowValuationRepository();
    await _mockConnectivityCheck('wifi');
    final propertyBloc = PropertyBloc(propertyRepository);
    final syncBloc = SyncBloc(
      propertyRepository,
      valuationRepository,
      _FlowApiClient((path, _) async {
        return Response(
          requestOptions: RequestOptions(path: path),
          statusCode: 200,
          data: {'id': 501},
        );
      }),
      Connectivity(),
    );

    await tester.pumpWidget(
      _buildPropertyList(
        propertyBloc,
        syncBloc: syncBloc,
        valuationBloc: ValuationBloc(valuationRepository),
      ),
    );
    syncBloc.add(const ConnectivityChanged(true));
    propertyBloc.add(LoadProperties());
    await tester.pump(const Duration(milliseconds: 100));
    await propertyRepository.createProperty(
      const Property(
        address: 'Bole boundary test',
        propertyType: 'Residential',
        boundary:
            'POLYGON((8.9900 38.7600, 8.9901 38.7602, 8.9904 38.7604, 8.9900 38.7600))',
        areaSqm: 120,
        createdAt: '2026-05-24T00:00:00Z',
        updatedAt: '2026-05-24T00:00:00Z',
      ),
    );
    propertyBloc.add(LoadProperties());
    for (var i = 0; i < 8; i += 1) {
      await tester.pump(const Duration(milliseconds: 100));
      if (propertyRepository.snapshot().any(
            (property) => property.address == 'Bole boundary test',
          )) {
        break;
      }
    }
    expect(
      propertyRepository.snapshot().any(
            (property) => property.address == 'Bole boundary test',
          ),
      isTrue,
    );

    for (var i = 0; i < 8; i += 1) {
      await tester.pump(const Duration(milliseconds: 100));
      if (syncBloc.state.isOnline) {
        break;
      }
    }
    expect(syncBloc.state.isOnline, isTrue);

    syncBloc.add(SyncTriggered());
    for (var i = 0; i < 8; i += 1) {
      await tester.pump(const Duration(milliseconds: 100));
      if (syncBloc.state.status == SyncStatus.synced ||
          syncBloc.state.status == SyncStatus.failed) {
        break;
      }
    }
    expect(
      syncBloc.state.status,
      isNot(SyncStatus.syncing),
    );
    if (syncBloc.state.status == SyncStatus.failed) {
      expect(syncBloc.state.message, isNotNull);
      fail('sync blocked: ${syncBloc.state.message}');
    }

    expect(propertyRepository.syncUpdateCount, isPositive);
    expect(
      propertyRepository.snapshot().any(
            (property) => property.syncStatus == 'synced',
          ),
      isTrue,
    );
  });

  testWidgets('14.2 Low network simulation recovers and sync succeeds',
      (WidgetTester tester) async {
    final propertyRepository = _FlowPropertyRepository([
      const Property(
        id: 41,
        address: 'Kazanchis recovery path',
        propertyType: 'Commercial',
        boundary:
            'POLYGON((8.9980 38.7700, 8.9981 38.7702, 8.9984 38.7704, 8.9980 38.7700))',
        areaSqm: 210,
        syncStatus: 'pending',
        createdAt: '2026-05-24T00:00:00Z',
        updatedAt: '2026-05-24T00:00:00Z',
      ),
    ]);
    final valuationRepository = _FlowValuationRepository();
    await _mockConnectivityCheck('wifi');
    final syncBloc = SyncBloc(
      propertyRepository,
      valuationRepository,
      _FlowApiClient((path, _) async {
        return Response(
          requestOptions: RequestOptions(path: path),
          statusCode: 200,
          data: {'id': 9041},
        );
      }),
      Connectivity(),
    );

    await tester.pumpWidget(
      _buildPropertyList(
        PropertyBloc(propertyRepository),
        syncBloc: syncBloc,
        valuationBloc: ValuationBloc(valuationRepository),
      ),
    );

    for (var i = 0; i < 6; i += 1) {
      await tester.pump(const Duration(milliseconds: 100));
      if (!syncBloc.state.isOnline) {
        break;
      }
    }

    syncBloc.add(const ConnectivityChanged(false));
    await tester.pump(const Duration(milliseconds: 100));
    syncBloc.add(SyncTriggered());
    await tester.pump(const Duration(milliseconds: 150));
    expect(syncBloc.state.status, SyncStatus.failed);
    expect(syncBloc.state.message, contains('Reconnect and retry'));

    syncBloc.add(const ConnectivityChanged(true));
    for (var i = 0; i < 6; i += 1) {
      await tester.pump(const Duration(milliseconds: 100));
      if (syncBloc.state.isOnline) {
        break;
      }
    }

    syncBloc.add(SyncTriggered());
    for (var i = 0; i < 12; i += 1) {
      await tester.pump(const Duration(milliseconds: 150));
      if (syncBloc.state.status == SyncStatus.synced) {
        break;
      }
    }
    expect(syncBloc.state.status, SyncStatus.synced);
    expect(
      propertyRepository.snapshot().any(
            (property) => property.syncStatus == 'synced',
          ),
      isTrue,
    );
  });

  testWidgets(
      '13.3 Detail can add valuation and photo, then restart preserves data',
      (WidgetTester tester) async {
    final property = _sampleProperty().copyWith(id: 8);
    final propertyRepository = _FlowPropertyRepository([property]);
    final valuationRepository = _FlowValuationRepository();
    final syncBloc = _TestSyncBloc();
    final photoRepository = _TestPhotoRepository();
    final originalPhotoRepository = blocProviders.photoRepository;
    blocProviders.photoRepository = photoRepository;

    try {
      await tester.pumpWidget(
        _buildPropertyDetailHarness(
          property: property,
          propertyRepository: propertyRepository,
          valuationRepository: valuationRepository,
          syncBloc: syncBloc,
        ),
      );
      await tester.pump(const Duration(milliseconds: 120));

      final valuationBloc = tester
          .element(find.byType(PropertyDetailScreen))
          .read<ValuationBloc>();
      valuationBloc.add(
        const CreateNextValuation(
          propertyId: 8,
          marketValue: 145000,
          taxableValue: 118000,
        ),
      );
      valuationBloc.add(const LoadValuations(8));
      await tester.pump(const Duration(milliseconds: 300));
      await blocProviders.photoRepository.addPhoto(
        const Photo(
          propertyId: 8,
          filePath: '/tmp/valuadis-test-photo.jpg',
          createdAt: '2026-05-24T00:00:00Z',
        ),
      );
      await tester.pump(const Duration(milliseconds: 250));
      expect(await photoRepository.getPhotosForProperty(8), isNotEmpty);
      expect(
        valuationRepository.snapshot().any(
              (valuation) => valuation.marketValue == 145000,
            ),
        isTrue,
      );

      await tester.pumpWidget(
        _buildPropertyDetailHarness(
          property: property,
          propertyRepository: propertyRepository,
          valuationRepository: valuationRepository,
          syncBloc: syncBloc,
        ),
      );
      await tester.pump(const Duration(milliseconds: 200));
      expect(
        valuationRepository.snapshot().any(
              (valuation) => valuation.marketValue == 145000,
            ),
        isTrue,
      );
      expect(await photoRepository.getPhotosForProperty(8), isNotEmpty);
    } finally {
      blocProviders.photoRepository = originalPhotoRepository;
    }
  });

  testWidgets('14.3 Accessibility and layout checks hold under text scaling',
      (WidgetTester tester) async {
    final longProperty = _sampleProperty().copyWith(
      id: 77,
      address:
          'Very long Addis Ababa district label that should still render cleanly across narrow mobile layouts without overflow',
    );

    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(
          size: Size(375, 812),
          textScaler: TextScaler.linear(1.4),
        ),
        child: Directionality(
          textDirection: TextDirection.rtl,
          child: MaterialApp(
            home: Scaffold(
              body: PropertyCard(property: longProperty, onTap: () {}),
            ),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(tester.takeException(), isNull);

    final propertyCardFinder = find.byType(PropertyCard);
    expect(propertyCardFinder, findsOneWidget);
    expect(tester.getSize(propertyCardFinder).height, greaterThanOrEqualTo(48));
  });

  testWidgets('14.3 Login actions keep 48dp tap targets',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(
          size: Size(375, 812),
          textScaler: TextScaler.linear(1.3),
        ),
        child: _buildLoginScreen(_TestAuthRepository()),
      ),
    );
    await tester.pump();

    final offlineButton = find.ancestor(
      of: find.text('Continue offline'),
      matching: find.byType(OutlinedButton),
    );
    expect(offlineButton, findsOneWidget);
    expect(tester.getSize(offlineButton).height, greaterThanOrEqualTo(48));
  });

  testWidgets('Property list shell renders bottom navigation',
      (WidgetTester tester) async {
    final syncBloc = _TestSyncBloc();
    await tester.pumpWidget(_buildPropertyListScreen(syncBloc: syncBloc));

    expect(find.byType(BottomNavigationBar), findsOneWidget);
    expect(find.text('Properties'), findsOneWidget);
    expect(find.text('Map'), findsOneWidget);
    expect(find.text('New'), findsOneWidget);
  });
}
