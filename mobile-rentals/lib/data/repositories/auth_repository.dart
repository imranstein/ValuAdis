import 'package:dio/dio.dart';

import '../api/api_client.dart';
import '../api/token_storage.dart';
import '../models/session_user.dart';

class AuthResult {
  const AuthResult.success(this.user)
      : ok = true,
        message = null;
  const AuthResult.failure(this.message)
      : ok = false,
        user = null;

  final bool ok;
  final SessionUser? user;
  final String? message;
}

/// Auth against the shared /api/v1/auth surface plus the citizen /rentals/signup
/// path. Mobile keeps the refresh token in the keystore (the web cookie flow is
/// untouched). Signup returns only an access token in the body, so we follow it
/// with a normal login to obtain the rotatable refresh token, no backend change.
class AuthRepository {
  AuthRepository(this._client, this._storage);

  final ApiClient _client;
  final TokenStorage _storage;

  Future<bool> hasSession() => _storage.hasSession;

  Future<AuthResult> login(String email, String password) async {
    try {
      final res = await _client.post('/auth/login',
          data: {'email': email, 'password': password});
      final stored = await _storeTokensFrom(res.data);
      if (!stored) return const AuthResult.failure('Unexpected login response.');
      final user = await fetchMe();
      return AuthResult.success(user ?? const SessionUser(accountType: AccountType.unknown));
    } on DioException catch (e) {
      return AuthResult.failure(_message(e, fallback: 'Login failed. Check your email and password.'));
    }
  }

  Future<AuthResult> signup({
    required String fullName,
    required String email,
    required String phone,
    required String password,
    required String municipality,
    required String faydaId,
    required AccountType accountType,
  }) async {
    final accountTypeStr =
        accountType == AccountType.propertyOwner ? 'property_owner' : 'renter';
    try {
      await _client.post('/rentals/signup', data: {
        'full_name': fullName,
        'email': email,
        'phone': phone,
        'password': password,
        'municipality': municipality,
        'fayda_id_number': faydaId,
        'account_type': accountTypeStr,
      });
      // Establish the full token pair (incl. refresh) through login.
      return login(email, password);
    } on DioException catch (e) {
      return AuthResult.failure(_message(e, fallback: 'Could not create your account.'));
    }
  }

  Future<SessionUser?> fetchMe() async {
    try {
      final res = await _client.get('/auth/me');
      final data = res.data;
      if (data is! Map<String, dynamic>) return null;
      final fallback =
          SessionUser.typeFromString(await _storage.readAccountType());
      return SessionUser.fromMeJson(data, fallbackType: fallback);
    } on DioException {
      return null;
    }
  }

  Future<void> logout() async {
    try {
      await _client.post('/auth/logout');
    } on DioException {
      // Logout always succeeds locally; server revocation is best-effort.
    }
    await _storage.clear();
  }

  Future<bool> _storeTokensFrom(dynamic payload) async {
    if (payload is! Map<String, dynamic>) return false;
    final data = payload['data'] is Map<String, dynamic>
        ? payload['data'] as Map<String, dynamic>
        : payload;
    final access = data['access_token'] as String?;
    if (access == null || access.isEmpty) return false;
    await _storage.saveTokens(
      accessToken: access,
      refreshToken: data['refresh_token'] as String?,
      accountType: data['account_type'] as String?,
    );
    return true;
  }

  String _message(DioException e, {required String fallback}) {
    final data = e.response?.data;
    if (data is Map && data['message'] is String) return data['message'] as String;
    if (data is Map && data['detail'] is String) return data['detail'] as String;
    return fallback;
  }
}
