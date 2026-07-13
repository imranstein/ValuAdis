import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/services.dart';

class HiveHelper {
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  static final FlutterSecureStorage _storage = const FlutterSecureStorage();
  static String? _cachedAccessToken;
  static String? _cachedRefreshToken;

  static Future<void> init() async {
    _cachedAccessToken = await _safeRead(_accessTokenKey);
    _cachedRefreshToken = await _safeRead(_refreshTokenKey);
  }

  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _safeWrite(_accessTokenKey, accessToken);
    await _safeWrite(_refreshTokenKey, refreshToken);
    _cachedAccessToken = accessToken;
    _cachedRefreshToken = refreshToken;
  }

  static String? getAccessToken() {
    return _cachedAccessToken;
  }

  static String? getRefreshToken() {
    return _cachedRefreshToken;
  }

  static Future<void> clearAuth() async {
    _cachedAccessToken = null;
    _cachedRefreshToken = null;
    await _safeDelete(_accessTokenKey);
    await _safeDelete(_refreshTokenKey);
  }

  static Future<String?> _safeRead(String key) async {
    try {
      return await _storage.read(key: key);
    } on PlatformException {
      return null;
    }
  }

  static Future<void> _safeWrite(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } on PlatformException {
      // Keep auth state in memory when secure storage is unavailable in test/runtime envs.
    }
  }

  static Future<void> _safeDelete(String key) async {
    try {
      await _storage.delete(key: key);
    } on PlatformException {
      // Keep auth lifecycle functional when secure storage is unavailable in test/runtime envs.
    }
  }
}
