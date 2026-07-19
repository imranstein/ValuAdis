import 'package:equatable/equatable.dart';

import '../../data/models/vehicle.dart';

enum VehicleStatus { initial, loading, loaded, error }

enum VehicleDetailStatus { initial, loading, loaded, error }

class VehicleState extends Equatable {
  final VehicleStatus status;
  final List<Vehicle> vehicles;
  final VehicleDetailStatus detailStatus;
  final Vehicle? selected;
  final String? message;

  const VehicleState({
    this.status = VehicleStatus.initial,
    this.vehicles = const [],
    this.detailStatus = VehicleDetailStatus.initial,
    this.selected,
    this.message,
  });

  VehicleState copyWith({
    VehicleStatus? status,
    List<Vehicle>? vehicles,
    VehicleDetailStatus? detailStatus,
    Vehicle? selected,
    String? message,
  }) {
    return VehicleState(
      status: status ?? this.status,
      vehicles: vehicles ?? this.vehicles,
      detailStatus: detailStatus ?? this.detailStatus,
      selected: selected ?? this.selected,
      message: message ?? this.message,
    );
  }

  @override
  List<Object?> get props => [
        status,
        vehicles,
        detailStatus,
        selected,
        message,
      ];
}
