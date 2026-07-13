import 'package:equatable/equatable.dart';

class Photo extends Equatable {
  final int? id;
  final int propertyId;
  final String filePath;
  final String syncStatus;
  final String createdAt;

  const Photo({
    this.id,
    required this.propertyId,
    required this.filePath,
    this.syncStatus = 'pending',
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'property_id': propertyId,
      'file_path': filePath,
      'sync_status': syncStatus,
      'created_at': createdAt,
    };
  }

  factory Photo.fromMap(Map<String, dynamic> map) {
    return Photo(
      id: map['id'] as int?,
      propertyId: map['property_id'] as int,
      filePath: map['file_path'] as String,
      syncStatus: map['sync_status'] as String? ?? 'pending',
      createdAt: map['created_at'] as String,
    );
  }

  Photo copyWith({
    int? id,
    int? propertyId,
    String? filePath,
    String? syncStatus,
    String? createdAt,
  }) {
    return Photo(
      id: id ?? this.id,
      propertyId: propertyId ?? this.propertyId,
      filePath: filePath ?? this.filePath,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [id, propertyId, filePath, syncStatus, createdAt];
}
