import 'package:flutter/foundation.dart';

/// App-wide constants and the release-safe API base resolver.
///
/// Mirrors the valuer app's `AppConstants.resolveApiBaseUrl` guard: a release
/// build that ships a missing or localhost API base is a packaging error and
/// fails loudly rather than silently talking to a developer machine.
class AppConstants {
  AppConstants._();

  static const String appName = 'ValuAdis Rent';

  // Addis Ababa center — map default.
  static const double defaultLat = 9.0320;
  static const double defaultLon = 38.7578;
  static const double defaultZoom = 13.0;

  static const List<double> ethiopiaLatRange = [3.0, 15.0];
  static const List<double> ethiopiaLonRange = [33.0, 48.0];

  /// Pilot sub-cities lead the list (plan: Bole + Yeka), rest follow.
  static const List<String> addisSubCities = [
    'Bole',
    'Yeka',
    'Kirkos',
    'Lideta',
    'Arada',
    'Addis Ketema',
    'Gullele',
    'Kolfe Keranio',
    'Nifas Silk-Lafto',
    'Akaky Kaliti',
    'Lemi Kura',
  ];

  static const List<String> propertyTypes = [
    'residential',
    'mixed_use',
  ];

  static const Map<String, List<String>> subtypesByType = {
    'residential': [
      'apartment',
      'condominium',
      'villa',
      'single_family',
      'townhouse',
      'studio',
    ],
    'mixed_use': [
      'apartment',
    ],
  };

  static const List<String> conditions = [
    'excellent',
    'very_good',
    'good',
    'fair',
    'needs_repair',
  ];

  static const String _localApiBaseUrl = 'http://localhost:8000';

  static String get apiBaseUrl => resolveApiBaseUrl(
        const String.fromEnvironment('API_BASE_URL', defaultValue: ''),
        kReleaseMode,
      );

  static String get apiBase => '$apiBaseUrl/api/v1';

  /// Resolves the API base for the current build mode. Debug/profile fall back
  /// to localhost; a release build with a missing or local base throws.
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

  static bool _isLocalUrl(String url) =>
      url.contains('localhost') ||
      url.contains('127.0.0.1') ||
      url.contains('10.0.2.2');

  /// Local polling interval for status-change notifications (no push infra v1).
  static const Duration notificationPollInterval = Duration(seconds: 90);

  /// Mirrors the backend's PropertyPhotoService limits (validated server-side
  /// too; checking client-side just gives an honest error before the upload).
  static const int maxPhotosPerProperty = 8;
  static const int maxPhotoSizeBytes = 5 * 1024 * 1024;
}
