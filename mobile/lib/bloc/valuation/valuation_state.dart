import 'package:equatable/equatable.dart';

import '../../data/models/valuation.dart';

enum ValuationStatus { initial, loading, loaded, error }

class ValuationState extends Equatable {
  final ValuationStatus status;
  final int? propertyId;
  final List<Valuation> valuations;
  final String? message;

  const ValuationState({
    this.status = ValuationStatus.initial,
    this.propertyId,
    this.valuations = const [],
    this.message,
  });

  ValuationState copyWith({
    ValuationStatus? status,
    int? propertyId,
    List<Valuation>? valuations,
    String? message,
  }) {
    return ValuationState(
      status: status ?? this.status,
      propertyId: propertyId ?? this.propertyId,
      valuations: valuations ?? this.valuations,
      message: message,
    );
  }

  @override
  List<Object?> get props => [status, propertyId, valuations, message];
}
