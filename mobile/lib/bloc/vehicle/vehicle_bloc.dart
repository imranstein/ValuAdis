import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/repositories/vehicle_repository.dart';
import 'vehicle_event.dart';
import 'vehicle_state.dart';

class VehicleBloc extends Bloc<VehicleEvent, VehicleState> {
  final VehicleRepository _repository;

  VehicleBloc(this._repository) : super(const VehicleState()) {
    on<LoadVehicles>(_onLoadVehicles);
    on<LoadVehicleDetail>(_onLoadVehicleDetail);
  }

  Future<void> _onLoadVehicles(
    LoadVehicles event,
    Emitter<VehicleState> emit,
  ) async {
    emit(state.copyWith(status: VehicleStatus.loading, message: null));
    try {
      final vehicles = await _repository.getVehicles();
      emit(state.copyWith(status: VehicleStatus.loaded, vehicles: vehicles));
    } catch (error) {
      emit(
        state.copyWith(
          status: VehicleStatus.error,
          message: _messageFor(error),
        ),
      );
    }
  }

  Future<void> _onLoadVehicleDetail(
    LoadVehicleDetail event,
    Emitter<VehicleState> emit,
  ) async {
    emit(
      state.copyWith(detailStatus: VehicleDetailStatus.loading, message: null),
    );
    try {
      final vehicle = await _repository.getVehicleById(event.vehicleId);
      emit(
        state.copyWith(
          detailStatus: VehicleDetailStatus.loaded,
          selected: vehicle,
        ),
      );
    } catch (error) {
      emit(
        state.copyWith(
          detailStatus: VehicleDetailStatus.error,
          message: _messageFor(error),
        ),
      );
    }
  }

  String _messageFor(Object error) {
    if (error is DioException) {
      // ApiClient rewrites DioException.error to a user-safe string.
      final safe = error.error;
      if (safe is String && safe.isNotEmpty) return safe;
      return 'Could not load vehicles. Check your connection and retry.';
    }
    return 'Could not load vehicles. Check your connection and retry.';
  }
}
