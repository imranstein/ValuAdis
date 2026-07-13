import 'package:equatable/equatable.dart';

class Valuation extends Equatable {
  final int? id;
  final int? serverId;
  final int propertyId;
  final double marketValue;
  final double taxableValue;
  final String syncStatus;
  final String createdAt;

  const Valuation({
    this.id,
    this.serverId,
    required this.propertyId,
    required this.marketValue,
    required this.taxableValue,
    this.syncStatus = 'pending',
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'server_id': serverId,
      'property_id': propertyId,
      'market_value': marketValue,
      'taxable_value': taxableValue,
      'sync_status': syncStatus,
      'created_at': createdAt,
    };
  }

  factory Valuation.fromMap(Map<String, dynamic> map) {
    return Valuation(
      id: map['id'] as int?,
      serverId: map['server_id'] as int?,
      propertyId: map['property_id'] as int,
      marketValue: (map['market_value'] as num).toDouble(),
      taxableValue: (map['taxable_value'] as num).toDouble(),
      syncStatus: map['sync_status'] as String? ?? 'pending',
      createdAt: map['created_at'] as String,
    );
  }

  Valuation copyWith({
    int? id,
    int? serverId,
    int? propertyId,
    double? marketValue,
    double? taxableValue,
    String? syncStatus,
    String? createdAt,
  }) {
    return Valuation(
      id: id ?? this.id,
      serverId: serverId ?? this.serverId,
      propertyId: propertyId ?? this.propertyId,
      marketValue: marketValue ?? this.marketValue,
      taxableValue: taxableValue ?? this.taxableValue,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
    id,
    serverId,
    propertyId,
    marketValue,
    taxableValue,
    syncStatus,
    createdAt,
  ];
}
