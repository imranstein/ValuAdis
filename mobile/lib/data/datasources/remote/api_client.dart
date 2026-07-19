import 'package:crypto/crypto.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../../../core/constants.dart';
import '../../datasources/local/hive_helper.dart';

class ApiClient {
  static const String _refreshPath = '/auth/refresh';
  static const String _retriedAfterRefreshFlag = 'retriedAfterRefresh';
  static const String _sessionExpiredMessage =
      'Session expired. Please sign in again.';

  late final Dio _dio;
  late final Dio _refreshDio;
  void Function(String message)? onUnauthorized;
  final int _maxRetries;
  final Duration _requestTimeout;
  final bool _enableSslPinning;
  final String? _pinnedSha256;
  Future<bool>? _refreshInFlight;

  ApiClient({
    this.onUnauthorized,
    int maxRetries = 2,
    Duration? requestTimeout,
    bool enableSslPinning = false,
    String? pinnedSha256,
  })  : _maxRetries = maxRetries,
        _requestTimeout = requestTimeout ?? const Duration(seconds: 30),
        _enableSslPinning = enableSslPinning,
        _pinnedSha256 = pinnedSha256 {
    final baseOptions = BaseOptions(
      baseUrl: AppConstants.apiBase,
      connectTimeout: _requestTimeout,
      receiveTimeout: _requestTimeout,
    );
    _dio = Dio(baseOptions);
    // Dedicated instance for token refresh: no interceptors, so a failing
    // refresh call can never trigger another refresh (loop guard).
    _refreshDio = Dio(baseOptions);

    if (_enableSslPinning) {
      _configureSslPinning(_dio, _pinnedSha256);
      _configureSslPinning(_refreshDio, _pinnedSha256);
    }

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = HiveHelper.getAccessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          final count = (options.extra['retryCount'] as int?) ?? 0;
          options.extra['retryCount'] = count;
          handler.next(options);
        },
        onError: (error, handler) async {
          final statusCode = error.response?.statusCode;

          if (statusCode == 401) {
            final options = error.requestOptions;
            final isRefreshRequest = options.path.contains(_refreshPath);
            final alreadyRetried =
                options.extra[_retriedAfterRefreshFlag] == true;

            if (!isRefreshRequest &&
                !alreadyRetried &&
                await _refreshTokensOnce()) {
              try {
                options.extra[_retriedAfterRefreshFlag] = true;
                final response = await _dio.fetch<dynamic>(options);
                return handler.resolve(response);
              } on DioException catch (retryError) {
                return handler.next(retryError);
              }
            }

            await HiveHelper.clearAuth();
            onUnauthorized?.call(_sessionExpiredMessage);
          }

          if (_shouldRetry(error)) {
            final count = (error.requestOptions.extra['retryCount'] as int?) ?? 0;
            if (count < _maxRetries) {
              return _retryRequest(error, count + 1, handler);
            }
          }

          final safeMessage = _safeErrorMessage(error);
          return handler.next(
            DioException(
              requestOptions: error.requestOptions,
              response: error.response,
              error: safeMessage,
              type: error.type,
              stackTrace: error.stackTrace,
            ),
          );
        },
      ),
    );
  }

  /// Attempts a single token refresh. Concurrent 401s share one in-flight
  /// refresh call instead of issuing duplicates.
  Future<bool> _refreshTokensOnce() {
    final inFlight = _refreshInFlight;
    if (inFlight != null) return inFlight;
    final refresh = _performTokenRefresh().whenComplete(() {
      _refreshInFlight = null;
    });
    _refreshInFlight = refresh;
    return refresh;
  }

  Future<bool> _performTokenRefresh() async {
    final refreshToken = HiveHelper.getRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) return false;

    try {
      final response = await _refreshDio.post<dynamic>(
        _refreshPath,
        options: Options(headers: {'Authorization': 'Bearer $refreshToken'}),
      );
      final payload = response.data;
      if (payload is! Map<String, dynamic>) return false;
      final data = payload['data'] is Map<String, dynamic>
          ? payload['data'] as Map<String, dynamic>
          : payload;
      final access = data['access_token'] as String?;
      final rotatedRefresh = data['refresh_token'] as String?;
      if (access == null || access.isEmpty) return false;

      await HiveHelper.saveTokens(
        accessToken: access,
        refreshToken: (rotatedRefresh == null || rotatedRefresh.isEmpty)
            ? refreshToken
            : rotatedRefresh,
      );
      return true;
    } on DioException {
      return false;
    }
  }

  @visibleForTesting
  void debugSetHttpClientAdapter(HttpClientAdapter adapter) {
    _dio.httpClientAdapter = adapter;
    _refreshDio.httpClientAdapter = adapter;
  }

  void _configureSslPinning(Dio dio, String? pinnedSha256) {
    final isEnabled = _enableSslPinning &&
        pinnedSha256 != null &&
        pinnedSha256.isNotEmpty;
    if (!isEnabled) return;

    final expected = pinnedSha256.toLowerCase();
    final adapter = dio.httpClientAdapter as dynamic;
    if (adapter.createHttpClient != null) {
      final previous = adapter.createHttpClient;
      adapter.createHttpClient = () {
        final client = previous();
        client.badCertificateCallback = (certificate, host, port) {
          final digest = sha256.convert(certificate.der).toString();
          return digest.toLowerCase() == expected;
        };
        return client;
      };
    }
  }

  void setUnauthorizedHandler(void Function(String message)? callback) {
    onUnauthorized = callback;
  }

  Future<void> _retryRequest(
    DioException error,
    int nextAttempt,
    ErrorInterceptorHandler handler,
  ) async {
    final options = error.requestOptions;
    final delayMs = 250 * (1 << (nextAttempt - 1));
    await Future<void>.delayed(Duration(milliseconds: delayMs));

    try {
      options.extra['retryCount'] = nextAttempt;
      final response = await _dio.fetch(options);
      return handler.resolve(response);
    } catch (e) {
      if (e is DioException) {
        if (nextAttempt < _maxRetries && _shouldRetry(e)) {
          return _retryRequest(e, nextAttempt + 1, handler);
        }
        final safeMessage = _safeErrorMessage(e);
        return handler.next(
          DioException(
            requestOptions: e.requestOptions,
            response: e.response,
            error: safeMessage,
            type: e.type,
            stackTrace: e.stackTrace,
          ),
        );
      }

      return handler.next(
        DioException(
          requestOptions: options,
          error: 'Request failed after retry',
          type: DioExceptionType.unknown,
        ),
      );
    }
  }

  String _safeErrorMessage(DioException error) {
    return switch (error.type) {
      DioExceptionType.connectionTimeout => 'Network timeout. Try again shortly.',
      DioExceptionType.sendTimeout => 'Network timeout. Try again shortly.',
      DioExceptionType.receiveTimeout => 'Network timeout. Try again shortly.',
      DioExceptionType.badResponse => switch (error.response?.statusCode) {
          400 => 'Unable to process the request. Please check your input.',
          401 => 'Session expired. Please sign in again.',
          500 => 'Server unavailable. Try again shortly.',
          _ => 'Request failed. Check your network and retry.',
        },
      _ => 'Request failed. Check your network and retry.',
    };
  }

  bool _shouldRetry(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return true;
    }

    final statusCode = error.response?.statusCode;
    return statusCode != null && statusCode >= 500;
  }

  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.get(path, queryParameters: queryParameters);
  }

  Future<Response<dynamic>> post(String path, {dynamic data}) async {
    return _dio.post(path, data: data);
  }

  Future<Response<dynamic>> put(String path, {dynamic data}) async {
    return _dio.put(path, data: data);
  }

  Future<Response<dynamic>> delete(String path) async {
    return _dio.delete(path);
  }
}
