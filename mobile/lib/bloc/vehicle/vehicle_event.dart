import 'package:equatable/equatable.dart';

abstract class VehicleEvent extends Equatable {
  const VehicleEvent();

  @override
  List<Object?> get props => [];
}

class LoadVehicles extends VehicleEvent {}

class LoadVehicleDetail extends VehicleEvent {
  final int vehicleId;

  const LoadVehicleDetail(this.vehicleId);

  @override
  List<Object?> get props => [vehicleId];
}
