import '../datasources/local/database_helper.dart';
import '../models/property.dart';

class PropertyRepository {
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

  Future<List<Property>> getAllProperties() async {
    final db = await _db.database;
    final maps = await db.query('properties', orderBy: 'updated_at DESC');
    return maps.map((m) => Property.fromMap(m)).toList();
  }

  Future<List<Property>> getPendingSync() async {
    final db = await _db.database;
    final now = DateTime.now().toIso8601String();
    final maps = await db.query(
      'properties',
      where:
          '(sync_status = ? AND (next_retry_at IS NULL OR next_retry_at <= ?))'
          ' OR (sync_status = ? AND next_retry_at IS NOT NULL AND next_retry_at <= ?)',
      whereArgs: ['pending', now, 'failed', now],
      orderBy: 'updated_at ASC',
    );
    return maps.map((m) => Property.fromMap(m)).toList();
  }

  Future<Property?> getById(int id) async {
    final db = await _db.database;
    final maps = await db.query('properties', where: 'id = ?', whereArgs: [id]);
    if (maps.isEmpty) return null;
    return Property.fromMap(maps.first);
  }

  Future<int> getRetryCount(int id) async {
    final db = await _db.database;
    final maps = await db.query(
      'properties',
      columns: ['retry_count'],
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );
    if (maps.isEmpty) return 0;
    return maps.first['retry_count'] as int? ?? 0;
  }

  Future<int> createProperty(Property property) async {
    final db = await _db.database;
    return db.insert('properties', property.toMap());
  }

  Future<int> updateSyncStatus(int id, String status) async {
    final db = await _db.database;
    return db.update(
      'properties',
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
      'properties',
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

  Future<int> updateProperty(Property property) async {
    if (property.id == null) {
      throw StateError('Cannot update property without local id');
    }

    final db = await _db.database;
    return db.update(
      'properties',
      property.toMap(),
      where: 'id = ?',
      whereArgs: [property.id],
    );
  }

  Future<int> updateServerId(int id, int serverId) async {
    final db = await _db.database;
    return db.update(
      'properties',
      {'server_id': serverId, 'sync_status': 'synced'},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<Property?> getByServerId(int serverId) async {
    final db = await _db.database;
    final maps = await db.query(
      'properties',
      where: 'server_id = ?',
      whereArgs: [serverId],
      limit: 1,
    );
    if (maps.isEmpty) return null;
    return Property.fromMap(maps.first);
  }

  /// Upserts a property pulled from the server, matched by [Property.serverId].
  ///
  /// - No local row for that server id -> insert as a synced record.
  /// - Existing local row already synced -> refresh it with server data.
  /// - Existing local row with pending/failed local changes -> skip, so a
  ///   server pull never clobbers work that has not been pushed yet.
  Future<void> upsertFromServer(Property serverProperty) async {
    final serverId = serverProperty.serverId;
    if (serverId == null) return;

    final existing = await getByServerId(serverId);
    if (existing == null) {
      await createProperty(serverProperty.copyWith(syncStatus: 'synced'));
      return;
    }

    if (existing.syncStatus != 'synced') return;

    await updateProperty(
      serverProperty.copyWith(id: existing.id, syncStatus: 'synced'),
    );
  }
}
