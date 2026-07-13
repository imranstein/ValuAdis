import '../datasources/local/database_helper.dart';
import '../models/valuation.dart';

class ValuationRepository {
  final DatabaseHelper _db = DatabaseHelper.instance;

  static const int _maxRetryAttempts = 10;

  Duration _retryDelay(int retryCount) {
    final seconds = 2 << retryCount;
    return Duration(seconds: seconds > 120 ? 120 : seconds);
  }

  String? _nextRetryAt(int retryCount) {
    if (retryCount <= 0) return null;
    final scheduledAt = DateTime.now().add(_retryDelay(retryCount));
    return scheduledAt.toIso8601String();
  }

  Future<int> createValuation(Valuation valuation) async {
    final db = await _db.database;
    return db.insert('valuations', valuation.toMap());
  }

  Future<List<Valuation>> getValuationsByPropertyId(int propertyId) async {
    final db = await _db.database;
    final maps = await db.query(
      'valuations',
      where: 'property_id = ?',
      whereArgs: [propertyId],
      orderBy: 'created_at DESC',
    );
    return maps.map((m) => Valuation.fromMap(m)).toList();
  }

  Future<int> getRetryCount(int id) async {
    final db = await _db.database;
    final maps = await db.query(
      'valuations',
      columns: ['retry_count'],
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );
    if (maps.isEmpty) return 0;
    return maps.first['retry_count'] as int? ?? 0;
  }

  Future<List<Valuation>> getPendingSync() async {
    final db = await _db.database;
    final now = DateTime.now().toIso8601String();
    final maps = await db.query(
      'valuations',
      where:
          '(sync_status = ? AND (next_retry_at IS NULL OR next_retry_at <= ?))'
          ' OR (sync_status = ? AND next_retry_at IS NOT NULL AND next_retry_at <= ?)',
      whereArgs: ['pending', now, 'failed', now],
      orderBy: 'created_at DESC',
    );
    return maps.map((m) => Valuation.fromMap(m)).toList();
  }

  Future<int> updateSyncStatus(int id, String status) async {
    final db = await _db.database;
    return db.update(
      'valuations',
      {
        'sync_status': status,
        'retry_count': 0,
        'last_failed_reason': null,
        'next_retry_at': null,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> markSyncFailure(int id, String reason, int retryCount) async {
    final db = await _db.database;
    final nextRetryCount = retryCount + 1;
    final nextRetryAt = nextRetryCount > _maxRetryAttempts
        ? null
        : _nextRetryAt(nextRetryCount);
    final nextRetryAtValue =
        nextRetryCount > _maxRetryAttempts
            ? DateTime.now().add(const Duration(hours: 1)).toIso8601String()
            : nextRetryAt;
    final nextStatus = nextRetryCount > _maxRetryAttempts ? 'failed' : 'pending';

    return db.update(
      'valuations',
      {
        'sync_status': nextStatus,
        'retry_count': nextRetryCount,
        'last_failed_reason': reason,
        'next_retry_at': nextRetryAtValue,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> updateServerId(int id, int serverId) async {
    final db = await _db.database;
    return db.update(
      'valuations',
      {'server_id': serverId, 'sync_status': 'synced'},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<Valuation?> getByServerId(int serverId) async {
    final db = await _db.database;
    final maps = await db.query(
      'valuations',
      where: 'server_id = ?',
      whereArgs: [serverId],
      limit: 1,
    );
    if (maps.isEmpty) return null;
    return Valuation.fromMap(maps.first);
  }

  Future<int> updateValuation(Valuation valuation) async {
    if (valuation.id == null) {
      throw StateError('Cannot update valuation without local id');
    }
    final db = await _db.database;
    return db.update(
      'valuations',
      valuation.toMap(),
      where: 'id = ?',
      whereArgs: [valuation.id],
    );
  }

  /// Upserts a valuation pulled from the server, matched by
  /// [Valuation.serverId]. Follows the same conflict rules as properties:
  /// insert when unseen, refresh when locally synced, and skip when the local
  /// row still has pending/failed (not-yet-pushed) changes.
  Future<void> upsertFromServer(Valuation serverValuation) async {
    final serverId = serverValuation.serverId;
    if (serverId == null) return;

    final existing = await getByServerId(serverId);
    if (existing == null) {
      await createValuation(serverValuation.copyWith(syncStatus: 'synced'));
      return;
    }

    if (existing.syncStatus != 'synced') return;

    await updateValuation(
      serverValuation.copyWith(id: existing.id, syncStatus: 'synced'),
    );
  }
}
