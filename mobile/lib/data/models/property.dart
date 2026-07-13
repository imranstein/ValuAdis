import 'package:equatable/equatable.dart';

class Property extends Equatable {
  final int? id;
  final int? serverId;
  final String address;
  final String propertyType;
  final String? boundary;
  final double areaSqm;
  final String syncStatus;
  final String createdAt;
  final String updatedAt;

  const Property({
    this.id,
    this.serverId,
    required this.address,
    required this.propertyType,
    this.boundary,
    required this.areaSqm,
    this.syncStatus = 'pending',
    required this.createdAt,
    required this.updatedAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'server_id': serverId,
      'address': address,
      'property_type': propertyType,
      'boundary': boundary,
      'area_sqm': areaSqm,
      'sync_status': syncStatus,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }

  factory Property.fromMap(Map<String, dynamic> map) {
    return Property(
      id: map['id'] as int?,
      serverId: map['server_id'] as int?,
      address: map['address'] as String,
      propertyType: map['property_type'] as String,
      boundary: map['boundary'] as String?,
      areaSqm: (map['area_sqm'] as num).toDouble(),
      syncStatus: map['sync_status'] as String? ?? 'pending',
      createdAt: map['created_at'] as String,
      updatedAt: map['updated_at'] as String,
    );
  }

  Property copyWith({
    int? id,
    int? serverId,
    String? address,
    String? propertyType,
    String? boundary,
    double? areaSqm,
    String? syncStatus,
    String? createdAt,
    String? updatedAt,
  }) {
    return Property(
      id: id ?? this.id,
      serverId: serverId ?? this.serverId,
      address: address ?? this.address,
      propertyType: propertyType ?? this.propertyType,
      boundary: boundary ?? this.boundary,
      areaSqm: areaSqm ?? this.areaSqm,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        serverId,
        address,
        propertyType,
        boundary,
        areaSqm,
        syncStatus,
        createdAt,
        updatedAt,
      ];
}
