import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Secure, persistent token storage. Unlike the web client (httpOnly refresh
/// cookie), the mobile client holds the refresh token in the platform keystore
/// and presents it as a bearer token to /auth/refresh. Access tokens survive a
/// cold start so the session is not lost on relaunch.
class TokenStorage {
  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  final FlutterSecureStorage _storage;

  static const _kAccess = 'valuadis_rent_access';
  static const _kRefresh = 'valuadis_rent_refresh';
  static const _kAccountType = 'valuadis_rent_account_type';

  String? _accessCache;

  Future<void> saveTokens({
    required String accessToken,
    String? refreshToken,
    String? accountType,
  }) async {
    _accessCache = accessToken;
    await _storage.write(key: _kAccess, value: accessToken);
    if (refreshToken != null && refreshToken.isNotEmpty) {
      await _storage.write(key: _kRefresh, value: refreshToken);
    }
    if (accountType != null && accountType.isNotEmpty) {
      await _storage.write(key: _kAccountType, value: accountType);
    }
  }

  Future<String?> readAccessToken() async {
    _accessCache ??= await _storage.read(key: _kAccess);
    return _accessCache;
  }

  Future<String?> readRefreshToken() => _storage.read(key: _kRefresh);

  Future<String?> readAccountType() => _storage.read(key: _kAccountType);

  Future<bool> get hasSession async =>
      (await readAccessToken())?.isNotEmpty ?? false;

  Future<void> clear() async {
    _accessCache = null;
    await _storage.delete(key: _kAccess);
    await _storage.delete(key: _kRefresh);
    await _storage.delete(key: _kAccountType);
  }
}
