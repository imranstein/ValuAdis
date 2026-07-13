import 'package:equatable/equatable.dart';

import '../../data/models/quick_valuation.dart';

enum QuickValuationStatus { initial, loading, success, failure }

class QuickValuationState extends Equatable {
  final QuickValuationStatus status;
  final QuickValuationResult? result;
  final String? message;

  const QuickValuationState({
    this.status = QuickValuationStatus.initial,
    this.result,
    this.message,
  });

  QuickValuationState copyWith({
    QuickValuationStatus? status,
    QuickValuationResult? result,
    String? message,
  }) {
    return QuickValuationState(
      status: status ?? this.status,
      result: result ?? this.result,
      message: message ?? this.message,
    );
  }

  @override
  List<Object?> get props => [status, result, message];
}
