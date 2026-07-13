import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/models/valuation.dart';
import '../../data/repositories/valuation_repository.dart';
import 'valuation_event.dart';
import 'valuation_state.dart';

class ValuationBloc extends Bloc<ValuationEvent, ValuationState> {
  final ValuationRepository _repository;

  ValuationBloc(this._repository) : super(const ValuationState()) {
    on<LoadValuations>(_onLoadValuations);
    on<CreateValuation>(_onCreateValuation);
    on<CreateNextValuation>(_onCreateNextValuation);
  }

  Future<void> _onLoadValuations(
    LoadValuations event,
    Emitter<ValuationState> emit,
  ) async {
    emit(state.copyWith(status: ValuationStatus.loading, propertyId: event.propertyId));
    try {
      final valuations = await _repository.getValuationsByPropertyId(event.propertyId);
      emit(
        state.copyWith(
          status: ValuationStatus.loaded,
          propertyId: event.propertyId,
          valuations: valuations,
          message: null,
        ),
      );
    } catch (e) {
      emit(
        state.copyWith(
          status: ValuationStatus.error,
          propertyId: event.propertyId,
          message: e.toString(),
        ),
      );
    }
  }

  Future<void> _onCreateValuation(
    CreateValuation event,
    Emitter<ValuationState> emit,
  ) async {
    try {
      final valuation = event.valuation.copyWith(
        syncStatus: 'pending',
      );
      await _repository.createValuation(valuation);
      add(LoadValuations(event.valuation.propertyId));
    } catch (e) {
      emit(state.copyWith(status: ValuationStatus.error, message: e.toString()));
    }
  }

  Future<void> _onCreateNextValuation(
    CreateNextValuation event,
    Emitter<ValuationState> emit,
  ) async {
    final valuation = Valuation(
      propertyId: event.propertyId,
      marketValue: event.marketValue,
      taxableValue: event.taxableValue,
      createdAt: DateTime.now().toIso8601String(),
      syncStatus: 'pending',
    );
    await _onCreateValuation(CreateValuation(valuation), emit);
  }
}
