import 'package:equatable/equatable.dart';

import '../../data/models/quick_valuation.dart';

abstract class QuickValuationEvent extends Equatable {
  const QuickValuationEvent();

  @override
  List<Object?> get props => [];
}

class QuickValuationRequested extends QuickValuationEvent {
  final QuickValuationRequest request;

  const QuickValuationRequested(this.request);

  @override
  List<Object?> get props => [request];
}

class QuickValuationReset extends QuickValuationEvent {}
