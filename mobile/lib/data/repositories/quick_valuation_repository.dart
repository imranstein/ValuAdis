import '../datasources/remote/api_client.dart';
import '../models/quick_valuation.dart';

/// Remote-backed repository for standalone quick valuations
/// (`POST /valuations/quick`). Reuses the shared authenticated [ApiClient].
class QuickValuationRepository {
  final ApiClient _apiClient;

  QuickValuationRepository(this._apiClient);

  Future<QuickValuationResult> calculate(QuickValuationRequest request) async {
    final response = await _apiClient.post(
      '/valuations/quick',
      data: request.toJson(),
    );
    final data = response.data;
    if (data is Map<String, dynamic>) {
      return QuickValuationResult.fromJson(data);
    }
    throw StateError('Unexpected quick valuation response');
  }
}
