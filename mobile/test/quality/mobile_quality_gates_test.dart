import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/services.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuadis/core/constants.dart';
import 'package:valuadis/data/datasources/local/hive_helper.dart';

import 'package:valuadis/bloc/auth/auth_bloc.dart';
import 'package:valuadis/bloc/auth/auth_event.dart';
import 'package:valuadis/bloc/auth/auth_state.dart';
import 'package:valuadis/bloc/property/property_bloc.dart';
import 'package:valuadis/bloc/property/property_event.dart';
import 'package:valuadis/bloc/sync/sync_bloc.dart';
import 'package:valuadis/bloc/sync/sync_event.dart';
import 'package:valuadis/bloc/sync/sync_state.dart';
import 'package:valuadis/bloc/quick_valuation/quick_valuation_bloc.dart';
import 'package:valuadis/bloc/quick_valuation/quick_valuation_event.dart';
import 'package:valuadis/bloc/quick_valuation/quick_valuation_state.dart';
import 'package:valuadis/bloc/vehicle/vehicle_bloc.dart';
import 'package:valuadis/bloc/vehicle/vehicle_event.dart';
import 'package:valuadis/bloc/vehicle/vehicle_state.dart';
import 'package:valuadis/data/datasources/remote/api_client.dart';
import 'package:valuadis/data/models/property.dart';
import 'package:valuadis/data/models/quick_valuation.dart';
import 'package:valuadis/data/models/valuation.dart';
import 'package:valuadis/data/models/vehicle.dart';
import 'package:valuadis/data/repositories/auth_repository.dart';
import 'package:valuadis/data/repositories/property_repository.dart';
import 'package:valuadis/data/repositories/quick_valuation_repository.dart';
import 'package:valuadis/data/repositories/valuation_repository.dart';
import 'package:valuadis/data/repositories/vehicle_repository.dart';

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

class _StubAuthRepository implements AuthRepository {
  bool _loggedIn;
  bool loginReturn;
  bool loginCalled = false;
  bool logoutCalled = false;
  bool offlineCalled = false;

  _StubAuthRepository({bool loggedIn = false, this.loginReturn = false})
      : _loggedIn = loggedIn;

  @override
  bool get isLoggedIn => _loggedIn;

  @override
  Future<bool> login(String email, String password) async {
    loginCalled = true;
    return loginReturn;
  }

  @override
  Future<void> logout() async {
    logoutCalled = true;
    _loggedIn = false;
  }

  @override
  Future<void> loginOffline() async {
    offlineCalled = true;
    _loggedIn = true;
  }
}

class _InMemoryPropertyRepository extends PropertyRepository {
  final List<Property> _properties = [];
  int _nextId = 1;
  final Map<int, String> _retryReasons = {};
  final Map<int, int> _retryCounts = {};

  @override
  Future<List<Property>> getAllProperties() async {
    return List<Property>.from(_properties);
  }

  @override
  Future<List<Property>> getPendingSync() async {
    return List<Property>.from(_properties);
  }

  @override
  Future<Property?> getById(int id) async {
    return _properties.where((property) => property.id == id).isEmpty
        ? null
        : _properties.firstWhere((property) => property.id == id);
  }

  @override
  Future<int> getRetryCount(int id) async {
    return _retryCounts[id] ?? 0;
  }

  @override
  Future<int> createProperty(Property property) async {
    final item =
        property.id == null ? property.copyWith(id: _nextId++) : property;
    _properties.add(item);
    return item.id!;
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    final index = _properties.indexWhere((item) => item.id == id);
    if (index == -1) return 0;
    final current = _properties[index];
    _properties[index] = current.copyWith(syncStatus: status);
    if (status == 'synced') {
      _retryCounts[id] = 0;
      _retryReasons[id] = '';
    }
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    _retryCounts[id] = retryCount + 1;
    _retryReasons[id] = reason;
    final index = _properties.indexWhere((item) => item.id == id);
    if (index != -1) {
      _properties[index] = _properties[index].copyWith(syncStatus: 'failed');
    }
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
}

class _InMemoryValuationRepository extends ValuationRepository {
  final List<Valuation> _valuations = [];
  int _nextId = 1;
  final Map<int, int> _retryCounts = {};

  @override
  Future<int> createValuation(Valuation valuation) async {
    final item =
        valuation.id == null ? valuation.copyWith(id: _nextId++) : valuation;
    _valuations.add(item);
    return item.id!;
  }

  @override
  Future<List<Valuation>> getValuationsByPropertyId(int propertyId) async {
    return _valuations
        .where((valuation) => valuation.propertyId == propertyId)
        .toList();
  }

  @override
  Future<int> getRetryCount(int id) async => _retryCounts[id] ?? 0;

  @override
  Future<List<Valuation>> getPendingSync() async {
    return List<Valuation>.from(_valuations);
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    final index = _valuations.indexWhere((item) => item.id == id);
    if (index == -1) return 0;
    _valuations[index] = _valuations[index].copyWith(syncStatus: status);
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    _retryCounts[id] = retryCount + 1;
    return 1;
  }
}

class _FakePropertyBlocRepo extends PropertyRepository {
  _FakePropertyBlocRepo(this._seed);

  final List<Property> _seed;
  bool loadCalled = false;
  bool createCalled = false;
  bool updateCalled = false;

  @override
  Future<List<Property>> getAllProperties() async {
    loadCalled = true;
    return List<Property>.from(_seed);
  }

  @override
  Future<int> createProperty(Property property) async {
    createCalled = true;
    _seed.add(property);
    return 1;
  }

  @override
  Future<int> updateProperty(Property property) async {
    updateCalled = true;
    return 1;
  }
}

class _FakePropertySyncRepo extends PropertyRepository {
  _FakePropertySyncRepo(this.pendingProperties);

  final List<Property> pendingProperties;
  int updateSyncStatusCount = 0;
  int markSyncFailureCount = 0;
  int loadPendingCount = 0;

  @override
  Future<List<Property>> getPendingSync() async {
    loadPendingCount += 1;
    return List<Property>.from(pendingProperties);
  }

  @override
  Future<int> getRetryCount(int id) async {
    return 0;
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    updateSyncStatusCount += 1;
    return 1;
  }

  @override
  Future<int> updateServerId(int id, int serverId) async {
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    markSyncFailureCount += 1;
    return 1;
  }

  @override
  Future<List<Property>> getAllProperties() async => const [];
}

class _OfflineStartupPropertySyncRepo extends PropertyRepository {
  _OfflineStartupPropertySyncRepo({
    required List<Property> cachedProperties,
    DateTime? now,
    this.staleAfter = const Duration(days: 30),
  })  : _cachedProperties = cachedProperties,
        _now = now ?? DateTime.now();

  final List<Property> _cachedProperties;
  final DateTime _now;
  final Duration staleAfter;
  int syncQueryCount = 0;
  int getAllCount = 0;
  int updateSyncStatusCount = 0;

  bool _isFresh(Property property) {
    try {
      final updatedAt = DateTime.parse(property.updatedAt);
      return _now.difference(updatedAt) <= staleAfter;
    } catch (_) {
      return true;
    }
  }

  @override
  Future<List<Property>> getPendingSync() async {
    syncQueryCount += 1;
    return _cachedProperties.where(_isFresh).toList();
  }

  @override
  Future<List<Property>> getAllProperties() async {
    getAllCount += 1;
    return List<Property>.from(_cachedProperties);
  }

  @override
  Future<int> getRetryCount(int id) async {
    return 0;
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    updateSyncStatusCount += 1;
    return 1;
  }

  @override
  Future<int> updateServerId(int id, int serverId) async {
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    return 1;
  }
}

class _FakeValuationSyncRepo extends ValuationRepository {
  _FakeValuationSyncRepo(this.pendingValuations);

  final List<Valuation> pendingValuations;
  int updateSyncStatusCount = 0;
  int markSyncFailureCount = 0;
  int loadPendingCount = 0;

  @override
  Future<List<Valuation>> getPendingSync() async {
    loadPendingCount += 1;
    return List<Valuation>.from(pendingValuations);
  }

  @override
  Future<int> getRetryCount(int id) async {
    return 0;
  }

  @override
  Future<List<Valuation>> getValuationsByPropertyId(int propertyId) async {
    return pendingValuations
        .where((item) => item.propertyId == propertyId)
        .toList(growable: false);
  }

  @override
  Future<int> updateSyncStatus(int id, String status) async {
    updateSyncStatusCount += 1;
    return 1;
  }

  @override
  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    markSyncFailureCount += 1;
    return 1;
  }
}

/// In-memory property repository that overrides only the storage primitives,
/// so the production [PropertyRepository.upsertFromServer] conflict logic runs
/// unchanged (insert-new / refresh-synced / skip-unsynced) without a database.
/// getPendingSync returns empty so these tests isolate the pull phase.
class _PullPropertyRepo extends PropertyRepository {
  _PullPropertyRepo(this._items);

  final List<Property> _items;
  int _nextId = 1000;

  List<Property> get items => List<Property>.unmodifiable(_items);

  @override
  Future<List<Property>> getPendingSync() async => const [];

  @override
  Future<List<Property>> getAllProperties() async => List<Property>.from(_items);

  @override
  Future<Property?> getByServerId(int serverId) async {
    final matches = _items.where((p) => p.serverId == serverId);
    return matches.isEmpty ? null : matches.first;
  }

  @override
  Future<int> createProperty(Property property) async {
    final item = property.copyWith(id: _nextId++);
    _items.add(item);
    return item.id!;
  }

  @override
  Future<int> updateProperty(Property property) async {
    final index = _items.indexWhere((p) => p.id == property.id);
    if (index == -1) return 0;
    _items[index] = property;
    return 1;
  }
}

class _ReleaseGatedAuthRepository extends _StubAuthRepository {
  @override
  Future<void> loginOffline() {
    throw StateError('Offline demo login is unavailable in release builds.');
  }
}

class _ScriptedHttpAdapter implements HttpClientAdapter {
  _ScriptedHttpAdapter(this.onFetch);

  final Future<ResponseBody> Function(RequestOptions options) onFetch;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) {
    return onFetch(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _jsonBody(Object payload, int statusCode) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: {
      Headers.contentTypeHeader: [Headers.jsonContentType],
    },
  );
}

class _StubSyncApiClient extends ApiClient {
  _StubSyncApiClient(this.handlePost, {this.handleGet});

  final Future<Response<dynamic>> Function(String path, dynamic data)
      handlePost;

  /// Pull requests are stubbed too so the two-way sync stays network-free.
  /// Defaults to an empty server payload when a test does not script pulls.
  final Future<Response<dynamic>> Function(String path)? handleGet;

  @override
  Future<Response> post(String path, {dynamic data}) {
    return handlePost(path, data);
  }

  @override
  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) {
    final scripted = handleGet;
    if (scripted != null) return scripted(path);
    return Future.value(
      Response<dynamic>(
        requestOptions: RequestOptions(path: path),
        statusCode: 200,
        data: {'success': true, 'data': <dynamic>[]},
      ),
    );
  }
}

class _StubVehicleRepository extends VehicleRepository {
  _StubVehicleRepository({this.vehicles = const [], this.error})
      : super(ApiClient());

  final List<Vehicle> vehicles;
  final Object? error;
  bool getVehiclesCalled = false;
  int? detailRequestedId;

  @override
  Future<List<Vehicle>> getVehicles() async {
    getVehiclesCalled = true;
    final failure = error;
    if (failure != null) throw failure;
    return vehicles;
  }

  @override
  Future<Vehicle> getVehicleById(int id) async {
    detailRequestedId = id;
    final failure = error;
    if (failure != null) throw failure;
    return vehicles.firstWhere((vehicle) => vehicle.id == id);
  }
}

class _StubQuickValuationRepository extends QuickValuationRepository {
  _StubQuickValuationRepository({this.result, this.error})
      : super(ApiClient());

  final QuickValuationResult? result;
  final Object? error;
  QuickValuationRequest? lastRequest;

  @override
  Future<QuickValuationResult> calculate(QuickValuationRequest request) async {
    lastRequest = request;
    final failure = error;
    if (failure != null) throw failure;
    return result!;
  }
}

Vehicle _buildVehicle(int id) {
  return Vehicle(
    id: id,
    userId: 1,
    make: 'Toyota',
    model: 'Corolla',
    year: 2020,
    vin: '1HGCM82633A004352',
    plateNumber: 'AA-12345',
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
  );
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('12.1 Repository tests', () {
    test('Auth repository offline login/logout updates token state', () async {
      final stubRepo = _StubAuthRepository();

      await stubRepo.loginOffline();
      expect(stubRepo.isLoggedIn, isTrue);
      await stubRepo.logout();
      expect(stubRepo.isLoggedIn, isFalse);
    });

    test('Property repository CRUD and sync helpers', () async {
      final repository = _InMemoryPropertyRepository();

      final now = DateTime.now().toIso8601String();
      final property = Property(
        address: 'Test property',
        propertyType: 'House',
        areaSqm: 120,
        createdAt: now,
        updatedAt: now,
      );

      final id = await repository.createProperty(property);
      final items = await repository.getAllProperties();
      expect(items.length, equals(1));
      expect(items.first.id, equals(id));

      final pending = await repository.getPendingSync();
      expect(pending.length, equals(1));

      final loaded = await repository.getById(id);
      expect(loaded, isNotNull);
      expect(loaded!.address, equals('Test property'));

      final retryCount = await repository.getRetryCount(id);
      expect(retryCount, equals(0));
    });

    test('Valuation repository persists and loads by property', () async {
      final repository = _InMemoryValuationRepository();

      final valuation = Valuation(
        propertyId: 1,
        marketValue: 100000,
        taxableValue: 90000,
        createdAt: DateTime.now().toIso8601String(),
      );
      await repository.createValuation(valuation);
      final items = await repository.getValuationsByPropertyId(1);
      expect(items.length, equals(1));
      expect(items.first.marketValue, equals(100000));
    });
  });

  group('12.2 Bloc tests', () {
    test('AuthBloc emits loading then success/failure states', () async {
      final repo = _StubAuthRepository(loginReturn: true);
      final bloc = AuthBloc(repo);

      final seen = <AuthState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(
        const AuthLoginRequested(
            email: 'test@example.com', password: 'password'),
      );
      await Future<void>.delayed(const Duration(milliseconds: 80));
      await sub.cancel();

      expect(
        seen.any(
          (state) => state.status == AuthStatus.loading,
        ),
        isTrue,
      );
      expect(
        seen.any(
          (state) =>
              state.status == AuthStatus.authenticated && state.message == null,
        ),
        isTrue,
      );

      expect(seen.length >= 2, isTrue);
    });

    test('AuthBloc offline request emits authenticated', () async {
      final repo = _StubAuthRepository();
      final bloc = AuthBloc(repo);

      final seen = <AuthState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(AuthOfflineRequested());
      await Future<void>.delayed(const Duration(milliseconds: 10));

      expect(seen.last.status, AuthStatus.authenticated);
      expect(repo.offlineCalled, isTrue);
      await sub.cancel();
    });

    test('PropertyBloc loads properties and creates item', () async {
      final repo = _FakePropertyBlocRepo(const []);
      final bloc = PropertyBloc(repo);

      bloc.add(LoadProperties());
      await Future<void>.delayed(const Duration(milliseconds: 20));
      expect(repo.loadCalled, isTrue);

      bloc.add(
        const CreateProperty(
          Property(
            address: 'New',
            propertyType: 'House',
            areaSqm: 77,
            createdAt: '2026-01-01T00:00:00Z',
            updatedAt: '2026-01-01T00:00:00Z',
          ),
        ),
      );

      await Future<void>.delayed(const Duration(milliseconds: 20));
      expect(repo.createCalled, isTrue);
    });

    test('SyncBloc blocks sync while offline', () async {
      final propertyRepository = _FakePropertySyncRepo(const []);
      final valuationRepository = _FakeValuationSyncRepo(const []);
      await _mockConnectivityCheck('none');
      final api = _StubSyncApiClient((_, __) async {
        throw StateError('Should not be called offline');
      });

      final bloc = SyncBloc(
        propertyRepository,
        valuationRepository,
        api,
        Connectivity(),
      );

      bloc.add(const ConnectivityChanged(false));
      await Future<void>.delayed(const Duration(milliseconds: 20));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 20));

      expect(bloc.state.status, SyncStatus.failed);
      expect(bloc.state.message, 'No network detected. Reconnect and retry.');
    });

    test('SyncBloc completes when pending items sync successfully', () async {
      final propertyRepository = _FakePropertySyncRepo([
        const Property(
          id: 1,
          address: 'Test',
          propertyType: 'House',
          areaSqm: 77,
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        ),
      ]);
      final valuationRepository = _FakeValuationSyncRepo([
        const Valuation(
          id: 11,
          propertyId: 1,
          marketValue: 1000,
          taxableValue: 900,
          createdAt: '2026-01-01T00:00:00Z',
        ),
      ]);
      final api = _StubSyncApiClient((path, _) async {
        return Response(
          requestOptions: RequestOptions(path: path),
          statusCode: 200,
        data: path.contains('properties') ? {'id': 201} : <String, dynamic>{},
      );
    });
      await _mockConnectivityCheck('wifi');

      final bloc = SyncBloc(
        propertyRepository,
        valuationRepository,
        api,
        Connectivity(),
      );

      bloc.add(const ConnectivityChanged(true));
      await Future<void>.delayed(const Duration(milliseconds: 20));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 60));

      expect(
        bloc.state.status,
        anyOf(SyncStatus.synced, SyncStatus.syncing),
      );
    });

    test('EC-M01 surfaces session expiry as auth failure state', () async {
      final repo = _StubAuthRepository(loggedIn: true);
      final bloc = AuthBloc(repo);

      final seen = <AuthState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(
        const AuthSessionExpired(message: 'Session expired. Please sign in again.'),
      );

      await Future<void>.delayed(const Duration(milliseconds: 20));
      expect(repo.logoutCalled, isTrue);
      expect(seen.last.status, AuthStatus.failure);
      expect(seen.last.message, 'Session expired. Please sign in again.');
      await sub.cancel();
    });

    test('EC-M02 handles connectivity churn without dropping pending work', () async {
      final propertyRepository = _FakePropertySyncRepo([
        const Property(
          id: 15,
          address: 'Offline Boundary Property',
          propertyType: 'Residential',
          areaSqm: 80,
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        ),
      ]);
      final valuationRepository = _FakeValuationSyncRepo(const []);

      var syncCalls = 0;
      final api = _StubSyncApiClient((path, _) async {
        syncCalls += 1;
        return Response(
          requestOptions: RequestOptions(path: path),
          statusCode: 200,
          data: path.contains('properties') ? {'id': 301} : <String, dynamic>{},
        );
      });

      await _mockConnectivityCheck('none');
      final bloc = SyncBloc(
        propertyRepository,
        valuationRepository,
        api,
        Connectivity(),
      );

      bloc.add(const ConnectivityChanged(false));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 40));
      expect(bloc.state.status, SyncStatus.failed);

      bloc.add(const ConnectivityChanged(true));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 80));
      expect(syncCalls, greaterThanOrEqualTo(1));
      expect(bloc.state.status, isIn(<SyncStatus>[SyncStatus.synced, SyncStatus.syncing]));

      bloc.add(const ConnectivityChanged(false));
      await Future<void>.delayed(const Duration(milliseconds: 20));
      bloc.add(const ConnectivityChanged(true));
      await Future<void>.delayed(const Duration(milliseconds: 80));
      expect(syncCalls, greaterThanOrEqualTo(1));
      expect(bloc.state.status, isIn(<SyncStatus>[SyncStatus.synced, SyncStatus.syncing]));
    });

    test('EC-M03 handles backend 5xx response as sync failure', () async {
      final propertyRepository = _FakePropertySyncRepo([
        const Property(
          id: 21,
          address: 'Failure Property',
          propertyType: 'Commercial',
          areaSqm: 90,
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        ),
      ]);
      final valuationRepository = _FakeValuationSyncRepo(const []);

      final api = _StubSyncApiClient((path, _) async {
        throw DioException(
          requestOptions: RequestOptions(path: path),
          response: Response(
            requestOptions: RequestOptions(path: path),
            statusCode: 500,
          ),
          type: DioExceptionType.badResponse,
        );
      });

      await _mockConnectivityCheck('wifi');
      final bloc = SyncBloc(
        propertyRepository,
        valuationRepository,
        api,
        Connectivity(),
      );

      bloc.add(const ConnectivityChanged(true));
      await Future<void>.delayed(const Duration(milliseconds: 20));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 80));

      expect(bloc.state.status, SyncStatus.failed);
      expect(bloc.state.message, contains('failed to sync'));
    });

    test('EC-M04 offline startup ignores stale cache entries', () async {
      final freshTime = DateTime.parse('2026-05-31T23:59:59.000Z');

      final repo = _OfflineStartupPropertySyncRepo(
        now: freshTime,
        staleAfter: const Duration(days: 1),
        cachedProperties: [
          const Property(
            id: 30,
            address: 'Very stale property',
            propertyType: 'Residential',
            areaSqm: 100,
            createdAt: '2026-01-01T00:00:00.000Z',
            updatedAt: '2026-01-01T00:00:00.000Z',
            syncStatus: 'pending',
          ),
          Property(
            id: 31,
            address: 'Boundary property',
            propertyType: 'Commercial',
            areaSqm: 150,
            createdAt: freshTime.toIso8601String(),
            updatedAt: freshTime.toIso8601String(),
            syncStatus: 'pending',
          ),
        ],
      );

      var syncCalls = 0;
      final api = _StubSyncApiClient((path, _) async {
        syncCalls += 1;
        return Response(
          requestOptions: RequestOptions(path: path),
          statusCode: 200,
          data: path.contains('properties') ? {'id': 902} : <String, dynamic>{},
        );
      });

      await _mockConnectivityCheck('wifi');
      final bloc = SyncBloc(
        repo,
        _FakeValuationSyncRepo(const []),
        api,
        Connectivity(),
      );

      await Future<void>.delayed(const Duration(milliseconds: 25));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 80));

      expect(syncCalls, equals(1));
      expect(repo.syncQueryCount, equals(1));
      expect(bloc.state.status, isNot(SyncStatus.failed));
      expect(repo.updateSyncStatusCount, equals(2));
    });
  });

  group('M1 token refresh', () {
    setUp(() async {
      FlutterSecureStorage.setMockInitialValues({});
      await HiveHelper.clearAuth();
    });

    test('EC-M01a 401 refreshes once and transparently retries the request',
        () async {
      await HiveHelper.saveTokens(
        accessToken: 'expired-access',
        refreshToken: 'refresh-1',
      );
      var unauthorizedCalls = 0;
      var refreshCalls = 0;
      var apiCalls = 0;

      final client = ApiClient(onUnauthorized: (_) => unauthorizedCalls++);
      client.debugSetHttpClientAdapter(_ScriptedHttpAdapter((options) async {
        if (options.path.contains('/auth/refresh')) {
          refreshCalls += 1;
          expect(options.headers['Authorization'], 'Bearer refresh-1');
          return _jsonBody({
            'success': true,
            'message': 'Token refreshed',
            'data': {
              'access_token': 'access-2',
              'refresh_token': 'refresh-2',
            },
          }, 200);
        }
        apiCalls += 1;
        if (options.headers['Authorization'] == 'Bearer expired-access') {
          return _jsonBody({'detail': 'Token expired'}, 401);
        }
        expect(options.headers['Authorization'], 'Bearer access-2');
        return _jsonBody({'items': <dynamic>[]}, 200);
      }));

      final response = await client.get('/properties');

      expect(response.statusCode, 200);
      expect(refreshCalls, 1);
      expect(apiCalls, 2);
      expect(unauthorizedCalls, 0);
      expect(HiveHelper.getAccessToken(), 'access-2');
      expect(HiveHelper.getRefreshToken(), 'refresh-2');
    });

    test('EC-M01b failed refresh clears auth and forces re-login', () async {
      await HiveHelper.saveTokens(
        accessToken: 'expired-access',
        refreshToken: 'stale-refresh',
      );
      final unauthorizedMessages = <String>[];
      var refreshCalls = 0;

      final client = ApiClient(onUnauthorized: unauthorizedMessages.add);
      client.debugSetHttpClientAdapter(_ScriptedHttpAdapter((options) async {
        if (options.path.contains('/auth/refresh')) {
          refreshCalls += 1;
          return _jsonBody({'detail': 'Invalid refresh token'}, 401);
        }
        return _jsonBody({'detail': 'Token expired'}, 401);
      }));

      await expectLater(
        client.get('/properties'),
        throwsA(isA<DioException>()),
      );
      expect(refreshCalls, 1);
      expect(
        unauthorizedMessages,
        ['Session expired. Please sign in again.'],
      );
      expect(HiveHelper.getAccessToken(), isNull);
      expect(HiveHelper.getRefreshToken(), isNull);
    });

    test('EC-M01c retried request that 401s again does not refresh twice',
        () async {
      await HiveHelper.saveTokens(
        accessToken: 'expired-access',
        refreshToken: 'refresh-1',
      );
      var unauthorizedCalls = 0;
      var refreshCalls = 0;

      final client = ApiClient(onUnauthorized: (_) => unauthorizedCalls++);
      client.debugSetHttpClientAdapter(_ScriptedHttpAdapter((options) async {
        if (options.path.contains('/auth/refresh')) {
          refreshCalls += 1;
          return _jsonBody({
            'success': true,
            'message': 'Token refreshed',
            'data': {
              'access_token': 'access-2',
              'refresh_token': 'refresh-2',
            },
          }, 200);
        }
        return _jsonBody({'detail': 'Still unauthorized'}, 401);
      }));

      await expectLater(
        client.get('/properties'),
        throwsA(isA<DioException>()),
      );
      expect(refreshCalls, 1);
      expect(unauthorizedCalls, 1);
      expect(HiveHelper.getAccessToken(), isNull);
    });
  });

  group('M2 offline demo gating', () {
    test('offline demo flag is enabled outside release builds', () {
      expect(AppConstants.allowOfflineDemo, isTrue);
    });

    test('AuthBloc surfaces failure when offline demo login is unavailable',
        () async {
      final repo = _ReleaseGatedAuthRepository();
      final bloc = AuthBloc(repo);

      final seen = <AuthState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(AuthOfflineRequested());
      await Future<void>.delayed(const Duration(milliseconds: 20));
      await sub.cancel();

      expect(seen.last.status, AuthStatus.failure);
      expect(
        seen.last.message,
        'Offline demo login is unavailable in release builds.',
      );
    });
  });

  group('12.3 Vehicle bloc', () {
    test('VehicleBloc load success emits loaded with vehicles', () async {
      final repo = _StubVehicleRepository(vehicles: [_buildVehicle(1)]);
      final bloc = VehicleBloc(repo);

      final seen = <VehicleState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(LoadVehicles());
      await Future<void>.delayed(const Duration(milliseconds: 20));
      await sub.cancel();

      expect(repo.getVehiclesCalled, isTrue);
      expect(seen.any((state) => state.status == VehicleStatus.loading), isTrue);
      final loaded = seen.last;
      expect(loaded.status, VehicleStatus.loaded);
      expect(loaded.vehicles.single.displayName, 'Toyota Corolla (2020)');
    });

    test('VehicleBloc load failure emits error with message', () async {
      final repo = _StubVehicleRepository(
        error: DioException(
          requestOptions: RequestOptions(path: '/vehicles'),
          error: 'Server unavailable. Try again shortly.',
        ),
      );
      final bloc = VehicleBloc(repo);

      final seen = <VehicleState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(LoadVehicles());
      await Future<void>.delayed(const Duration(milliseconds: 20));
      await sub.cancel();

      expect(seen.last.status, VehicleStatus.error);
      expect(seen.last.message, 'Server unavailable. Try again shortly.');
    });

    test('VehicleBloc detail load fetches by id via GET /vehicles/{id}',
        () async {
      final repo = _StubVehicleRepository(vehicles: [_buildVehicle(7)]);
      final bloc = VehicleBloc(repo);

      final seen = <VehicleState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(const LoadVehicleDetail(7));
      await Future<void>.delayed(const Duration(milliseconds: 20));
      await sub.cancel();

      expect(repo.detailRequestedId, 7);
      expect(seen.last.detailStatus, VehicleDetailStatus.loaded);
      expect(seen.last.selected?.id, 7);
    });
  });

  group('12.4 Quick valuation bloc', () {
    test('QuickValuationBloc success emits result with market/taxable value',
        () async {
      const result = QuickValuationResult(
        marketValue: 1000000,
        taxableValue: 250000,
        baseRate: 1000,
        multiplier: 1.0,
      );
      final repo = _StubQuickValuationRepository(result: result);
      final bloc = QuickValuationBloc(repo);

      final seen = <QuickValuationState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(
        const QuickValuationRequested(
          QuickValuationRequest(municipality: 'Addis Ababa', areaSqm: 100),
        ),
      );
      await Future<void>.delayed(const Duration(milliseconds: 20));
      await sub.cancel();

      expect(repo.lastRequest?.municipality, 'Addis Ababa');
      expect(seen.any((s) => s.status == QuickValuationStatus.loading), isTrue);
      expect(seen.last.status, QuickValuationStatus.success);
      expect(seen.last.result?.taxableValue, 250000);
    });

    test('QuickValuationBloc failure emits failure with message', () async {
      final repo = _StubQuickValuationRepository(
        error: DioException(
          requestOptions: RequestOptions(path: '/valuations/quick'),
          error: 'Unable to process the request. Please check your input.',
        ),
      );
      final bloc = QuickValuationBloc(repo);

      final seen = <QuickValuationState>[];
      final sub = bloc.stream.listen(seen.add);
      bloc.add(
        const QuickValuationRequested(
          QuickValuationRequest(municipality: 'Addis Ababa', areaSqm: 100),
        ),
      );
      await Future<void>.delayed(const Duration(milliseconds: 20));
      await sub.cancel();

      expect(seen.last.status, QuickValuationStatus.failure);
      expect(
        seen.last.message,
        'Unable to process the request. Please check your input.',
      );
    });
  });

  group('M3 two-way sync (server -> device pull)', () {
    Response<dynamic> serverList(String path, List<Map<String, dynamic>> data) {
      return Response<dynamic>(
        requestOptions: RequestOptions(path: path),
        statusCode: 200,
        data: {'success': true, 'data': data},
      );
    }

    _StubSyncApiClient pullApi(
      List<Map<String, dynamic>> properties, {
      bool failPull = false,
    }) {
      return _StubSyncApiClient(
        (path, _) async => Response(
          requestOptions: RequestOptions(path: path),
          statusCode: 200,
          data: <String, dynamic>{},
        ),
        handleGet: (path) async {
          if (failPull) {
            throw DioException(
              requestOptions: RequestOptions(path: path),
              type: DioExceptionType.connectionError,
            );
          }
          if (path.contains('propert')) {
            return serverList(path, properties);
          }
          return serverList(path, const []);
        },
      );
    }

    Future<SyncBloc> runSync(
      PropertyRepository propertyRepository,
      _StubSyncApiClient api,
    ) async {
      await _mockConnectivityCheck('wifi');
      final bloc = SyncBloc(
        propertyRepository,
        _FakeValuationSyncRepo(const []),
        api,
        Connectivity(),
      );
      bloc.add(const ConnectivityChanged(true));
      await Future<void>.delayed(const Duration(milliseconds: 20));
      bloc.add(SyncTriggered());
      await Future<void>.delayed(const Duration(milliseconds: 80));
      return bloc;
    }

    test('pull inserts new server records into local storage', () async {
      final repo = _PullPropertyRepo([]);
      final api = pullApi([
        {
          'id': 101,
          'address': 'Server Property A',
          'property_type': 'residential',
          'area_sqm': 120,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-01-01T00:00:00Z',
        },
        {
          'id': 102,
          'address': 'Server Property B',
          'property_type': 'commercial',
          'area_sqm': 240,
          'created_at': '2026-01-02T00:00:00Z',
          'updated_at': '2026-01-02T00:00:00Z',
        },
      ]);

      final bloc = await runSync(repo, api);

      expect(
        repo.items.map((p) => p.serverId).toList(),
        containsAll(<int>[101, 102]),
      );
      expect(bloc.state.status, SyncStatus.synced);
    });

    test('pull updates an existing local record matched by server id', () async {
      final repo = _PullPropertyRepo([
        const Property(
          id: 1,
          serverId: 50,
          address: 'Stale address',
          propertyType: 'residential',
          areaSqm: 100,
          syncStatus: 'synced',
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        ),
      ]);
      final api = pullApi([
        {
          'id': 50,
          'address': 'Refreshed address',
          'property_type': 'residential',
          'area_sqm': 175,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-01T00:00:00Z',
        },
      ]);

      await runSync(repo, api);

      expect(repo.items.length, equals(1));
      expect(repo.items.single.address, equals('Refreshed address'));
    });

    test('pull does not overwrite a local unsynced record', () async {
      final repo = _PullPropertyRepo([
        const Property(
          id: 2,
          serverId: 61,
          address: 'Local unsynced edit',
          propertyType: 'residential',
          areaSqm: 90,
          syncStatus: 'pending',
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-04-01T00:00:00Z',
        ),
      ]);
      final api = pullApi([
        {
          'id': 61,
          'address': 'Server version should be ignored',
          'property_type': 'commercial',
          'area_sqm': 500,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-01T00:00:00Z',
        },
      ]);

      await runSync(repo, api);

      expect(repo.items.single.address, equals('Local unsynced edit'));
    });

    test('pull failure leaves local data intact and emits failed state', () async {
      final repo = _PullPropertyRepo([
        const Property(
          id: 3,
          serverId: 70,
          address: 'Preserved on pull failure',
          propertyType: 'residential',
          areaSqm: 110,
          syncStatus: 'synced',
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        ),
      ]);
      final api = pullApi(const [], failPull: true);

      final bloc = await runSync(repo, api);

      expect(repo.items.single.address, equals('Preserved on pull failure'));
      expect(bloc.state.status, SyncStatus.failed);
    });
  });
}
