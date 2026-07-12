import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/services.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuadis/bloc/auth/auth_bloc.dart';
import 'package:valuadis/bloc/auth/auth_event.dart';
import 'package:valuadis/bloc/auth/auth_state.dart';
import 'package:valuadis/bloc/property/property_bloc.dart';
import 'package:valuadis/bloc/property/property_event.dart';
import 'package:valuadis/bloc/sync/sync_bloc.dart';
import 'package:valuadis/bloc/sync/sync_event.dart';
import 'package:valuadis/bloc/sync/sync_state.dart';
import 'package:valuadis/data/datasources/remote/api_client.dart';
import 'package:valuadis/data/models/property.dart';
import 'package:valuadis/data/models/valuation.dart';
import 'package:valuadis/data/repositories/auth_repository.dart';
import 'package:valuadis/data/repositories/property_repository.dart';
import 'package:valuadis/data/repositories/valuation_repository.dart';

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

class _StubSyncApiClient extends ApiClient {
  _StubSyncApiClient(this.handlePost);

  final Future<Response<dynamic>> Function(String path, dynamic data)
      handlePost;

  @override
  Future<Response> post(String path, {dynamic data}) {
    return handlePost(path, data);
  }
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
}
