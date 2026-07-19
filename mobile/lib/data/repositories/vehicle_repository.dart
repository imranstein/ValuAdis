import '../datasources/remote/api_client.dart';
import '../models/vehicle.dart';

/// Remote-backed repository for vehicles.
///
/// The backend exposes vehicles as a plain array (`GET /vehicles`) and a
/// single object (`GET /vehicles/{id}`); both go through the shared
/// [ApiClient], which injects the bearer token and handles token refresh.
class VehicleRepository {
  final ApiClient _apiClient;

  VehicleRepository(this._apiClient);

  Future<List<Vehicle>> getVehicles() async {
    final response = await _apiClient.get('/vehicles');
    return _parseVehicleList(response.data);
  }

  Future<Vehicle> getVehicleById(int id) async {
    final response = await _apiClient.get('/vehicles/$id');
    final data = response.data;
    if (data is Map<String, dynamic>) {
      return Vehicle.fromJson(data);
    }
    throw StateError('Unexpected vehicle detail response for id $id');
  }

  List<Vehicle> _parseVehicleList(dynamic data) {
    // Primary contract is a bare array; tolerate common envelopes.
    final items = switch (data) {
      List<dynamic>() => data,
      {'items': final List<dynamic> items} => items,
      {'data': final List<dynamic> items} => items,
      _ => const <dynamic>[],
    };
    return items
        .whereType<Map<String, dynamic>>()
        .map(Vehicle.fromJson)
        .toList(growable: false);
  }
}
