import 'package:dio/dio.dart';

import '../../core/constants.dart';
import 'token_storage.dart';

/// Thin dio wrapper with bearer auth and single-flight token refresh, mirroring
/// the valuer app's proven interceptor:
/// - attaches the access token on every request,
/// - on a 401, refreshes once via /auth/refresh (bearer = refresh token) and
///   retries the original request,
/// - a dedicated refresh dio has no interceptors, so a failing refresh can never
///   trigger another refresh (loop guard),
/// - concurrent 401s share one in-flight refresh.
class ApiClient {
  ApiClient(this._storage, {this.onUnauthorized}) {
    final options = BaseOptions(
      baseUrl: AppConstants.apiBase,
      connectTimeout: const Duration(seconds: 25),
      receiveTimeout: const Duration(seconds: 25),
      headers: {'Content-Type': 'application/json'},
    );
    _dio = Dio(options);
    _refreshDio = Dio(options);

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (opts, handler) async {
          final token = await _storage.readAccessToken();
          if (token != null && token.isNotEmpty) {
            opts.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(opts);
        },
        onError: (error, handler) async {
          final is401 = error.response?.statusCode == 401;
          final opts = error.requestOptions;
          final isRefresh = opts.path.contains(_refreshPath);
          final retried = opts.extra[_retriedFlag] == true;

          if (is401 && !isRefresh && !retried && await _refreshOnce()) {
            try {
              opts.extra[_retriedFlag] = true;
              final token = await _storage.readAccessToken();
              if (token != null) {
                opts.headers['Authorization'] = 'Bearer $token';
              }
              final response = await _dio.fetch<dynamic>(opts);
              return handler.resolve(response);
            } on DioException catch (retryError) {
              return handler.next(retryError);
            }
          }

          if (is401 && !isRefresh) {
            await _storage.clear();
            onUnauthorized?.call();
          }
          handler.next(error);
        },
      ),
    );
  }

  static const String _refreshPath = '/auth/refresh';
  static const String _retriedFlag = 'retriedAfterRefresh';

  final TokenStorage _storage;
  final void Function()? onUnauthorized;
  late final Dio _dio;
  late final Dio _refreshDio;
  Future<bool>? _refreshInFlight;

  Dio get raw => _dio;

  Future<Response<dynamic>> get(String path,
          {Map<String, dynamic>? query}) =>
      _dio.get(path, queryParameters: query);

  Future<Response<dynamic>> post(String path, {Object? data}) =>
      _dio.post(path, data: data);

  Future<Response<dynamic>> patch(String path, {Object? data}) =>
      _dio.patch(path, data: data);

  Future<Response<dynamic>> delete(String path) => _dio.delete(path);

  /// Multipart upload with progress (photo uploads); [data] must be a
  /// [FormData] built by the caller.
  Future<Response<dynamic>> postForm(
    String path, {
    required FormData data,
    void Function(int sent, int total)? onSendProgress,
  }) =>
      _dio.post(path, data: data, onSendProgress: onSendProgress);

  /// Bearer header for callers that need to fetch a protected resource
  /// (e.g. an `Image` widget) outside this client's own request pipeline.
  Future<Map<String, String>> authHeaders() async {
    final token = await _storage.readAccessToken();
    return (token == null || token.isEmpty) ? {} : {'Authorization': 'Bearer $token'};
  }

  Future<bool> _refreshOnce() {
    final inFlight = _refreshInFlight;
    if (inFlight != null) return inFlight;
    final future = _performRefresh().whenComplete(() {
      _refreshInFlight = null;
    });
    _refreshInFlight = future;
    return future;
  }

  Future<bool> _performRefresh() async {
    final refresh = await _storage.readRefreshToken();
    if (refresh == null || refresh.isEmpty) return false;
    try {
      final response = await _refreshDio.post(
        _refreshPath,
        options: Options(headers: {'Authorization': 'Bearer $refresh'}),
      );
      final payload = response.data;
      if (payload is! Map<String, dynamic>) return false;
      final data = payload['data'] is Map<String, dynamic>
          ? payload['data'] as Map<String, dynamic>
          : payload;
      final access = data['access_token'] as String?;
      if (access == null || access.isEmpty) return false;
      final rotated = data['refresh_token'] as String?;
      await _storage.saveTokens(
        accessToken: access,
        refreshToken: (rotated == null || rotated.isEmpty) ? refresh : rotated,
      );
      return true;
    } on DioException {
      return false;
    }
  }
}
