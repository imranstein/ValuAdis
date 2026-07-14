import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

import '../../../core/constants.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB(AppConstants.dbName);
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: AppConstants.dbVersion,
      onCreate: _createDB,
      onUpgrade: _upgradeDB,
      onOpen: (db) async {
        await _ensureBaseTables(db);
      },
    );
  }

  Future<void> _upgradeDB(
    Database db,
    int oldVersion,
    int newVersion,
  ) async {
    if (oldVersion < 2) {
      await _ensureBaseTables(db);
      await _addSyncMetadataColumns(db);
    }

    if (oldVersion < 3) {
      await _addValuationServerIdColumn(db);
    }

    if (oldVersion < 4) {
      await _addPropertyMunicipalityColumn(db);
    }
  }

  Future<void> _addPropertyMunicipalityColumn(Database db) async {
    final exists = (await db.rawQuery('PRAGMA table_info(properties)'))
        .any((row) => row['name'] == 'municipality');
    if (!exists) {
      await db.execute(
        "ALTER TABLE properties ADD COLUMN municipality TEXT NOT NULL DEFAULT 'Addis Ababa'",
      );
    }
  }

  Future<void> _ensureBaseTables(Database db) async {
    await db.execute('''
      CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        address TEXT NOT NULL,
        municipality TEXT NOT NULL DEFAULT 'Addis Ababa',
        property_type TEXT NOT NULL,
        boundary TEXT,
        area_sqm REAL NOT NULL,
        sync_status TEXT NOT NULL,
        retry_count INTEGER NOT NULL DEFAULT 0,
        last_failed_reason TEXT,
        next_retry_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        sync_status TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE IF NOT EXISTS valuations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        property_id INTEGER NOT NULL,
        market_value REAL NOT NULL,
        taxable_value REAL NOT NULL,
        sync_status TEXT NOT NULL,
        retry_count INTEGER NOT NULL DEFAULT 0,
        last_failed_reason TEXT,
        next_retry_at TEXT,
        created_at TEXT NOT NULL
      )
    ''');
  }

  Future<void> _addValuationServerIdColumn(Database db) async {
    final exists = (await db.rawQuery('PRAGMA table_info(valuations)'))
        .any((row) => row['name'] == 'server_id');
    if (!exists) {
      await db.execute('ALTER TABLE valuations ADD COLUMN server_id INTEGER');
    }
  }

  Future<void> _addSyncMetadataColumns(Database db) async {
    final columns = [
      const {
        'table': 'properties',
        'column': 'retry_count INTEGER NOT NULL DEFAULT 0',
      },
      const {
        'table': 'properties',
        'column': 'last_failed_reason TEXT',
      },
      const {
        'table': 'properties',
        'column': 'next_retry_at TEXT',
      },
      const {
        'table': 'valuations',
        'column': 'retry_count INTEGER NOT NULL DEFAULT 0',
      },
      const {
        'table': 'valuations',
        'column': 'last_failed_reason TEXT',
      },
      const {
        'table': 'valuations',
        'column': 'next_retry_at TEXT',
      },
    ];

    for (final entry in columns) {
      final table = entry['table'] as String;
      final def = entry['column'] as String;
      final columnName = def.split(' ').first;
      final exists =
          (await db.rawQuery('PRAGMA table_info($table)'))
              .any((row) => row['name'] == columnName);
      if (!exists) {
        await db.execute('ALTER TABLE $table ADD COLUMN $def');
      }
    }
  }

  Future<void> _createDB(Database db, int version) async {
    const idType = 'INTEGER PRIMARY KEY AUTOINCREMENT';
    const textType = 'TEXT NOT NULL';
    const intType = 'INTEGER NOT NULL';
    const realType = 'REAL NOT NULL';

      await db.execute('''
      CREATE TABLE properties (
        id $idType,
        server_id INTEGER,
        address $textType,
        municipality TEXT NOT NULL DEFAULT 'Addis Ababa',
        property_type $textType,
        boundary TEXT,
        area_sqm $realType,
        sync_status $textType,
        retry_count INTEGER NOT NULL DEFAULT 0,
        last_failed_reason TEXT,
        next_retry_at TEXT,
        created_at $textType,
        updated_at $textType
      )
    ''');

    await db.execute('''
      CREATE TABLE photos (
        id $idType,
        property_id $intType,
        file_path $textType,
        sync_status $textType,
        created_at $textType
      )
    ''');

    await db.execute('''
      CREATE TABLE valuations (
        id $idType,
        server_id INTEGER,
        property_id $intType,
        market_value $realType,
        taxable_value $realType,
        sync_status $textType,
        retry_count INTEGER NOT NULL DEFAULT 0,
        last_failed_reason TEXT,
        next_retry_at TEXT,
        created_at $textType
      )
    ''');
  }
}
