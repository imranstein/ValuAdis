import 'package:equatable/equatable.dart';

import '../../data/models/property.dart';

enum PropertyStatus { initial, loading, loaded, error }

class PropertyState extends Equatable {
  final PropertyStatus status;
  final List<Property> properties;
  final String? message;

  const PropertyState({
    this.status = PropertyStatus.initial,
    this.properties = const [],
    this.message,
  });

  PropertyState copyWith({
    PropertyStatus? status,
    List<Property>? properties,
    String? message,
  }) {
    return PropertyState(
      status: status ?? this.status,
      properties: properties ?? this.properties,
      message: message ?? this.message,
    );
  }

  @override
  List<Object?> get props => [status, properties, message];
}
