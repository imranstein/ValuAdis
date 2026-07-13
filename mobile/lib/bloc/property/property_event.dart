import 'package:equatable/equatable.dart';

import '../../data/models/property.dart';

abstract class PropertyEvent extends Equatable {
  const PropertyEvent();

  @override
  List<Object?> get props => [];
}

class LoadProperties extends PropertyEvent {}

class CreateProperty extends PropertyEvent {
  final Property property;

  const CreateProperty(this.property);

  @override
  List<Object?> get props => [property];
}

class SyncProperties extends PropertyEvent {}

class UpdateProperty extends PropertyEvent {
  final Property property;

  const UpdateProperty(this.property);

  @override
  List<Object?> get props => [property];
}
