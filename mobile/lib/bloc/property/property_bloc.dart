import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/repositories/property_repository.dart';
import 'property_event.dart';
import 'property_state.dart';

class PropertyBloc extends Bloc<PropertyEvent, PropertyState> {
  final PropertyRepository _repository;

  PropertyBloc(this._repository) : super(const PropertyState()) {
    on<LoadProperties>(_onLoadProperties);
    on<CreateProperty>(_onCreateProperty);
    on<SyncProperties>(_onSyncProperties);
    on<UpdateProperty>(_onUpdateProperty);
  }

  Future<void> _onLoadProperties(
    LoadProperties event,
    Emitter<PropertyState> emit,
  ) async {
    emit(state.copyWith(status: PropertyStatus.loading));
    try {
      final properties = await _repository.getAllProperties();
      emit(
        state.copyWith(status: PropertyStatus.loaded, properties: properties),
      );
    } catch (e) {
      emit(state.copyWith(status: PropertyStatus.error, message: e.toString()));
    }
  }

  Future<void> _onCreateProperty(
    CreateProperty event,
    Emitter<PropertyState> emit,
  ) async {
    try {
      final p = event.property.copyWith(syncStatus: 'pending');
      await _repository.createProperty(p);
      add(LoadProperties());
    } catch (e) {
      emit(state.copyWith(status: PropertyStatus.error, message: e.toString()));
    }
  }

  Future<void> _onSyncProperties(
    SyncProperties event,
    Emitter<PropertyState> emit,
  ) async {
    add(LoadProperties());
  }

  Future<void> _onUpdateProperty(
    UpdateProperty event,
    Emitter<PropertyState> emit,
  ) async {
    try {
      final updated =
          event.property.copyWith(updatedAt: DateTime.now().toIso8601String());
      await _repository.updateProperty(updated);
      add(LoadProperties());
    } catch (e) {
      emit(state.copyWith(status: PropertyStatus.error, message: e.toString()));
    }
  }
}
