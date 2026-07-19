import 'package:equatable/equatable.dart';

import '../../data/models/valuation.dart';

abstract class ValuationEvent extends Equatable {
  const ValuationEvent();

  @override
  List<Object?> get props => [];
}

class LoadValuations extends ValuationEvent {
  final int propertyId;

  const LoadValuations(this.propertyId);

  @override
  List<Object?> get props => [propertyId];
}

class CreateValuation extends ValuationEvent {
  final Valuation valuation;

  const CreateValuation(this.valuation);

  @override
  List<Object?> get props => [valuation];
}

class CreateNextValuation extends ValuationEvent {
  final int propertyId;
  final double marketValue;
  final double taxableValue;

  const CreateNextValuation({
    required this.propertyId,
    required this.marketValue,
    required this.taxableValue,
  });

  @override
  List<Object?> get props => [propertyId, marketValue, taxableValue];
}
