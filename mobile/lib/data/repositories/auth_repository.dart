import '../../core/constants.dart';
import '../datasources/local/hive_helper.dart';
import '../datasources/remote/api_client.dart';

class AuthRepository {
  final ApiClient _api = ApiClient();

  bool get isLoggedIn => HiveHelper.getAccessToken() != null;

  Future<bool> login(String email, String password) async {
    try {
      final response = await _api.post(
        '/auth/login',
        data: {'email': email, 'password': password},
      );
      final payload = response.data as Map<String, dynamic>;
      final data = payload['data'] is Map<String, dynamic>
          ? payload['data'] as Map<String, dynamic>
          : payload;
      final access = data['access_token'] as String?;
      final refresh = data['refresh_token'] as String?;
      if (access != null && refresh != null) {
        await HiveHelper.saveTokens(accessToken: access, refreshToken: refresh);
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<void> logout() async {
    await HiveHelper.clearAuth();
  }

  Future<void> loginOffline() async {
    if (!AppConstants.allowOfflineDemo) {
      throw StateError('Offline demo login is unavailable in release builds.');
    }
    await HiveHelper.saveTokens(
      accessToken: 'offline-demo-token',
      refreshToken: 'offline-demo-refresh',
    );
  }
}
