import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../core/geo.dart';
import '../../data/models/property.dart';
import '../../data/models/valuation.dart';
import '../../data/datasources/remote/api_client.dart';
import '../../data/repositories/property_repository.dart';
import '../../data/repositories/valuation_repository.dart';
import 'sync_event.dart';
import 'sync_state.dart';

class SyncBloc extends Bloc<SyncEvent, SyncState> {
  final PropertyRepository _propertyRepository;
  final ValuationRepository _valuationRepository;
  final ApiClient _apiClient;
  final Connectivity _connectivity;
  StreamSubscription<dynamic>? _connectivitySub;
  Timer? _periodicTimer;
  bool _syncInProgress = false;

  SyncBloc(
    this._propertyRepository,
    this._valuationRepository,
    this._apiClient, [
    Connectivity? connectivity,
    bool autoStartPeriodicSync = false,
    Duration? periodicSyncInterval,
  ])  : _connectivity = connectivity ?? Connectivity(),
        super(const SyncState()) {
    on<SyncTriggered>(_onSyncTriggered);
    on<SyncStatusRequested>(_onSyncStatusRequested);
    on<ConnectivityChanged>(_onConnectivityChanged);

    _observeConnectivity();
    if (autoStartPeriodicSync) {
      startPeriodicSync(
        periodicSyncInterval:
            periodicSyncInterval ?? const Duration(minutes: 15),
      );
    }
  }

  void startPeriodicSync({
    Duration periodicSyncInterval = const Duration(minutes: 15),
  }) {
    if (_periodicTimer != null) {
      return;
    }

    _periodicTimer = Timer.periodic(periodicSyncInterval, (_) {
      if (state.isOnline && state.status != SyncStatus.syncing) {
        add(SyncTriggered());
      }
    });
  }

  void stopPeriodicSync() {
    _periodicTimer?.cancel();
    _periodicTimer = null;
  }

  void _observeConnectivity() {
    _connectivitySub = _connectivity.onConnectivityChanged.listen((results) {
      final isOnline = !_isOffline(results);
      add(ConnectivityChanged(isOnline));
    });
    _connectivity.checkConnectivity().then(
          (results) => add(ConnectivityChanged(!_isOffline(results))),
        );
  }

  bool _isOffline(dynamic results) {
    if (results == null) return true;
    if (results is List<ConnectivityResult>) {
      return results.isEmpty ||
          (results.length == 1 && results.first == ConnectivityResult.none);
    }
    if (results is Iterable<ConnectivityResult>) {
      final list = results.toList();
      return list.isEmpty ||
          (list.length == 1 && list.first == ConnectivityResult.none);
    }
    if (results is ConnectivityResult) {
      return results == ConnectivityResult.none;
    }
    return true;
  }

  Future<void> _onSyncTriggered(
    SyncTriggered event,
    Emitter<SyncState> emit,
  ) async {
    // Rapid manual/connectivity triggers must not double-push the same
    // pending records; a trigger during an active sync is simply ignored.
    if (_syncInProgress) {
      return;
    }
    _syncInProgress = true;
    try {
      await _runSync(emit);
    } finally {
      _syncInProgress = false;
    }
  }

  Future<void> _runSync(Emitter<SyncState> emit) async {
    if (!state.isOnline) {
      emit(
        SyncState(
          status: SyncStatus.failed,
          isOnline: state.isOnline,
          pendingItems: 0,
          message: 'No network detected. Reconnect and retry.',
          itemStatuses: const [],
        ),
      );
      return;
    }

    final pendingProperties = await _propertyRepository.getPendingSync();
    final pendingValuations = await _valuationRepository.getPendingSync();
    final pendingTotal = pendingProperties.length + pendingValuations.length;

    emit(
      SyncState(
        status: SyncStatus.syncing,
        isOnline: state.isOnline,
        pendingItems: pendingTotal,
        message: 'Syncing pending data',
        itemStatuses: const [],
      ),
    );

    // Phase 1 (push): upload locally-created/edited records first, so a
    // just-pushed record comes back from the pull with its server id already
    // set and is deduplicated instead of duplicated.
    final itemStatuses = <SyncItemStatus>[];

    for (final property in pendingProperties) {
      await _syncProperty(itemStatuses, property, emit);
    }

    for (final valuation in pendingValuations) {
      await _syncValuation(itemStatuses, valuation, emit);
    }

    final hasPushFailures = itemStatuses.any((item) => item.status == 'failed');

    // Phase 2 (pull): fetch server state and upsert into local storage. A pull
    // failure must not lose the push result or corrupt local data, so it is
    // isolated and only downgrades the final status to failed.
    var pullFailed = false;
    try {
      await _pullServerState();
    } catch (error) {
      pullFailed = true;
    }

    final failed = hasPushFailures || pullFailed;
    emit(
      state.copyWith(
        status: failed ? SyncStatus.failed : SyncStatus.synced,
        pendingItems: 0,
        message: _finalMessage(
          hasPushFailures: hasPushFailures,
          pullFailed: pullFailed,
          pendingTotal: pendingTotal,
        ),
        itemStatuses: List.unmodifiable(itemStatuses),
      ),
    );
  }

  String _finalMessage({
    required bool hasPushFailures,
    required bool pullFailed,
    required int pendingTotal,
  }) {
    if (hasPushFailures) {
      return 'Some items failed to sync. Retry after backoff schedule.';
    }
    if (pullFailed) {
      return 'Server pull failed. Local data is intact; retry shortly.';
    }
    return pendingTotal == 0 ? 'No pending changes to sync.' : 'Sync complete';
  }

  /// Pulls server records and upserts them into local storage. Matching is by
  /// server id: unseen records are inserted, already-synced local rows are
  /// refreshed, and local rows with pending/failed changes are left untouched.
  Future<void> _pullServerState() async {
    await _pullProperties();
    await _pullValuations();
  }

  Future<void> _pullProperties() async {
    final response = await _apiClient.get('/properties');
    for (final raw in _extractRecords(response.data)) {
      final serverId = raw['id'];
      if (serverId is! int) continue;
      await _propertyRepository.upsertFromServer(_propertyFromServer(raw));
    }
  }

  Future<void> _pullValuations() async {
    final response = await _apiClient.get('/valuations');
    for (final raw in _extractRecords(response.data)) {
      final serverId = raw['id'];
      if (serverId is! int) continue;
      await _valuationRepository.upsertFromServer(_valuationFromServer(raw));
    }
  }

  List<Map<String, dynamic>> _extractRecords(dynamic data) {
    final list = data is List
        ? data
        : (data is Map && data['data'] is List)
            ? data['data'] as List
            : const [];
    return list
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList(growable: false);
  }

  Property _propertyFromServer(Map<String, dynamic> map) {
    final now = DateTime.now().toIso8601String();
    return Property(
      serverId: map['id'] as int,
      address: (map['address'] as String?) ?? '',
      municipality: (map['municipality'] as String?) ?? 'Addis Ababa',
      propertyType: (map['property_type'] as String?) ?? 'residential',
      boundary: map['boundary'] as String?,
      areaSqm: (map['area_sqm'] as num?)?.toDouble() ?? 0,
      syncStatus: 'synced',
      createdAt: (map['created_at'] as String?) ?? now,
      updatedAt: (map['updated_at'] as String?) ?? now,
    );
  }

  Valuation _valuationFromServer(Map<String, dynamic> map) {
    final now = DateTime.now().toIso8601String();
    return Valuation(
      serverId: map['id'] as int,
      propertyId: (map['property_id'] as num?)?.toInt() ?? 0,
      marketValue: (map['market_value'] as num?)?.toDouble() ?? 0,
      taxableValue: (map['taxable_value'] as num?)?.toDouble() ?? 0,
      syncStatus: 'synced',
      createdAt: (map['created_at'] as String?) ?? now,
    );
  }

  Future<void> _syncProperty(
    List<SyncItemStatus> itemStatuses,
    Property property,
    Emitter<SyncState> emit,
  ) async {
    if (property.id == null) {
      return;
    }

    final id = property.id!;
    _setItemStatus(
      itemStatuses,
      SyncItemStatus(
        scope: 'property',
        id: id,
        status: 'syncing',
        message: 'uploading',
      ),
    );
    emit(
      state.copyWith(
        itemStatuses: List.unmodifiable(itemStatuses),
      ),
    );

    try {
      await _propertyRepository.updateSyncStatus(id, 'syncing');
      final response = await _apiClient.post(
        '/properties',
        data: _propertyToJson(property),
      );
      if (response.data is Map<String, dynamic>) {
        final data = response.data as Map<String, dynamic>;
        // The create response nests the record under `data`
        // ({success, message, data: {id, ...}}); fall back to a flat id.
        final payload =
            data['data'] is Map<String, dynamic> ? data['data'] as Map : data;
        final serverId = payload['id'];
        if (serverId is int) {
          await _propertyRepository.updateServerId(id, serverId);
        }
        await _propertyRepository.updateSyncStatus(id, 'synced');
      } else {
        await _propertyRepository.updateSyncStatus(id, 'synced');
      }

      _setItemStatus(
        itemStatuses,
        SyncItemStatus(
          scope: 'property',
          id: id,
          status: 'synced',
          message: 'synced',
        ),
      );
    } catch (error) {
      final reason = _errorMessage(error);
      final retryCount = await _propertyRepository.getRetryCount(id);
      await _propertyRepository.markSyncFailure(id, reason, retryCount);
      _setItemStatus(
        itemStatuses,
        SyncItemStatus(
          scope: 'property',
          id: id,
          status: 'failed',
          message: reason,
        ),
      );
    }

    emit(
      state.copyWith(
        itemStatuses: List.unmodifiable(itemStatuses),
      ),
    );
  }

  Future<void> _syncValuation(
    List<SyncItemStatus> itemStatuses,
    Valuation valuation,
    Emitter<SyncState> emit,
  ) async {
    if (valuation.id == null) {
      return;
    }

    final id = valuation.id!;
    _setItemStatus(
      itemStatuses,
      SyncItemStatus(
        scope: 'valuation',
        id: id,
        status: 'syncing',
        message: 'uploading',
      ),
    );
    emit(
      state.copyWith(
        itemStatuses: List.unmodifiable(itemStatuses),
      ),
    );

    try {
      await _valuationRepository.updateSyncStatus(id, 'syncing');
      final response =
          await _apiClient.post('/valuations', data: _valuationToJson(valuation));
      if (response.data is Map<String, dynamic>) {
        final data = response.data as Map<String, dynamic>;
        final payload =
            data['data'] is Map<String, dynamic> ? data['data'] as Map : data;
        final serverId = payload['id'];
        if (serverId is int) {
          await _valuationRepository.updateServerId(id, serverId);
        }
      }
      await _valuationRepository.updateSyncStatus(id, 'synced');

      _setItemStatus(
        itemStatuses,
        SyncItemStatus(
          scope: 'valuation',
          id: id,
          status: 'synced',
          message: 'synced',
        ),
      );
    } catch (error) {
      final reason = _errorMessage(error);
      final retryCount = await _valuationRepository.getRetryCount(id);
      await _valuationRepository.markSyncFailure(id, reason, retryCount);
      _setItemStatus(
        itemStatuses,
        SyncItemStatus(
          scope: 'valuation',
          id: id,
          status: 'failed',
          message: reason,
        ),
      );
    }

    emit(
      state.copyWith(
        itemStatuses: List.unmodifiable(itemStatuses),
      ),
    );
  }

  void _setItemStatus(List<SyncItemStatus> values, SyncItemStatus next) {
    final existingIndex = values.indexWhere(
      (value) => value.scope == next.scope && value.id == next.id,
    );
    if (existingIndex >= 0) {
      values[existingIndex] = next;
    } else {
      values.add(next);
    }
  }

  void _onConnectivityChanged(
    ConnectivityChanged event,
    Emitter<SyncState> emit,
  ) {
    final wasOnline = state.isOnline;
    emit(
      state.copyWith(
        status: state.status,
        message: event.isOnline ? state.message : state.message,
        isOnline: event.isOnline,
      ),
    );

    if (!wasOnline && event.isOnline) {
      add(SyncTriggered());
    }
  }

  @override
  Future<void> close() {
    _connectivitySub?.cancel();
    stopPeriodicSync();
    return super.close();
  }

  void _onSyncStatusRequested(
    SyncStatusRequested event,
    Emitter<SyncState> emit,
  ) {
    emit(
      SyncState(
        status: SyncStatus.idle,
        isOnline: state.isOnline,
        pendingItems: 0,
        itemStatuses: state.itemStatuses,
        message: state.message,
      ),
    );
  }

  String _errorMessage(Object error) {
    if (error is DioException) {
      final statusCode = error.response?.statusCode;
      if (statusCode == null) {
        return 'Network error. Check your connection and retry.';
      }
      return switch (statusCode) {
        400 => 'Unable to process the request. Please check your input.',
        401 => 'Session expired. Please sign in again.',
        500 => 'Server unavailable. Try again shortly.',
        _ => 'Request failed. Check your network and retry.',
      };
    }

    return 'Request failed. Check your network and retry.';
  }

  Map<String, dynamic> _propertyToJson(Property p) {
    final coordinates = parseWktPolygon(p.boundary);
    return {
      'address': p.address,
      'municipality': p.municipality,
      'property_type': p.propertyType,
      'area_sqm': p.areaSqm,
      if (p.boundary != null) 'boundary': p.boundary,
      if (coordinates.isNotEmpty) 'coordinates': coordinates,
    };
  }

  Map<String, dynamic> _valuationToJson(Valuation valuation) {
    return {
      'property_id': valuation.propertyId,
      'market_value': valuation.marketValue,
      'taxable_value': valuation.taxableValue,
      'sync_status': valuation.syncStatus,
    };
  }
}
