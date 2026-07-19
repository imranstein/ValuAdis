import 'package:equatable/equatable.dart';

/// A stored property photo (mirrors the backend's PropertyPhotoOut). The URL
/// is opaque and relative to the API origin — never a filesystem path.
class PropertyPhoto extends Equatable {
  const PropertyPhoto({
    required this.id,
    required this.url,
    required this.position,
    this.createdAt,
  });

  final int id;
  final String url;
  final int position;
  final DateTime? createdAt;

  /// Cache-safe fetch URL. The backend reuses integer photo ids after a
  /// delete (SQLite id reuse), so the bare URL can collide with a stale
  /// cached image; versioning by upload time makes each upload a distinct
  /// cache entry. The backend route ignores the extra query parameter.
  String get versionedUrl => createdAt == null
      ? url
      : '$url?v=${createdAt!.millisecondsSinceEpoch}';

  factory PropertyPhoto.fromJson(Map<String, dynamic> json) {
    return PropertyPhoto(
      id: json['id'] as int,
      url: json['url'] as String,
      position: json['position'] as int? ?? 0,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.tryParse(json['created_at'].toString()),
    );
  }

  @override
  List<Object?> get props => [id, url, position, createdAt];
}
