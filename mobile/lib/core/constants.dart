import 'package:flutter/foundation.dart';

class AppConstants {
  AppConstants._();

  static const String appName = 'ValuAdis';
  static const String dbName = 'valuadis.db';
  static const int dbVersion = 4;

  static const double defaultMapLat = 9.0320;
  static const double defaultMapLon = 38.7578;
  static const double defaultMapZoom = 15.0;

  static const double ethiopiaLatMin = 3.0;
  static const double ethiopiaLatMax = 15.0;
  static const double ethiopiaLonMin = 33.0;
  static const double ethiopiaLonMax = 48.0;

  static const String _localApiBaseUrl = 'http://localhost:8000';

  static String get apiBaseUrl => resolveApiBaseUrl(
        const String.fromEnvironment('API_BASE_URL', defaultValue: ''),
        kReleaseMode,
      );
  static String get apiBase => '$apiBaseUrl/api/v1';

  /// Resolves the API base URL for the current build mode. Debug/profile
  /// builds fall back to localhost, but a release build with a missing or
  /// local API_BASE_URL is a packaging error, so it fails loudly instead of
  /// shipping an app that silently talks to a developer machine.
  static String resolveApiBaseUrl(String defined, bool isRelease) {
    final value = defined.isEmpty ? _localApiBaseUrl : defined;
    if (isRelease && _isLocalUrl(value)) {
      throw StateError(
        'API_BASE_URL must be provided via --dart-define for release builds '
        'and must not point at localhost.',
      );
    }
    return value;
  }

  static bool _isLocalUrl(String url) {
    return url.contains('localhost') ||
        url.contains('127.0.0.1') ||
        url.contains('10.0.2.2');
  }

  /// Offline demo login is a development convenience only. It is disabled in
  /// release builds unless VALUADIS_ALLOW_OFFLINE_DEMO=true is passed
  /// explicitly via --dart-define.
  static bool get allowOfflineDemo => const bool.fromEnvironment(
        'VALUADIS_ALLOW_OFFLINE_DEMO',
        defaultValue: !kReleaseMode,
      );

  static bool get enablePeriodicSync => const bool.fromEnvironment(
    'VALUADIS_ENABLE_PERIODIC_SYNC',
    defaultValue: false,
  );

  static Duration get periodicSyncInterval => Duration(
        seconds: const int.fromEnvironment(
          'VALUADIS_PERIODIC_SYNC_SECONDS',
          defaultValue: 15 * 60,
        ),
      );

  static bool get enableSslPinning => const bool.fromEnvironment(
    'VALUADIS_ENABLE_SSL_PINNING',
    defaultValue: false,
  );

  static String? get sslPinnedSha256 =>
      const String.fromEnvironment('VALUADIS_SSL_PINNED_SHA256', defaultValue: '');
}
