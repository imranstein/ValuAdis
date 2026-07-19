import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/repositories/quick_valuation_repository.dart';
import 'quick_valuation_event.dart';
import 'quick_valuation_state.dart';

class QuickValuationBloc
    extends Bloc<QuickValuationEvent, QuickValuationState> {
  final QuickValuationRepository _repository;

  QuickValuationBloc(this._repository) : super(const QuickValuationState()) {
    on<QuickValuationRequested>(_onRequested);
    on<QuickValuationReset>(_onReset);
  }

  Future<void> _onRequested(
    QuickValuationRequested event,
    Emitter<QuickValuationState> emit,
  ) async {
    emit(
      state.copyWith(status: QuickValuationStatus.loading, message: null),
    );
    try {
      final result = await _repository.calculate(event.request);
      emit(
        state.copyWith(status: QuickValuationStatus.success, result: result),
      );
    } catch (error) {
      emit(
        state.copyWith(
          status: QuickValuationStatus.failure,
          message: _messageFor(error),
        ),
      );
    }
  }

  void _onReset(QuickValuationReset event, Emitter<QuickValuationState> emit) {
    emit(const QuickValuationState());
  }

  String _messageFor(Object error) {
    if (error is DioException) {
      final safe = error.error;
      if (safe is String && safe.isNotEmpty) return safe;
      return 'Could not calculate valuation. Check your input and retry.';
    }
    return 'Could not calculate valuation. Check your input and retry.';
  }
}
