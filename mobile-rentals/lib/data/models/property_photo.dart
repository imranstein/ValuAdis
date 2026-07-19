import 'package:equatable/equatable.dart';

/// A stored property photo (mirrors the backend's PropertyPhotoOut). The URL
/// is opaque and relative to the API origin — never a filesystem path.
class PropertyPhoto extends Equatable {
  const PropertyPhoto({required this.id, required this.url, required this.position});

  final int id;
  final String url;
  final int position;

  factory PropertyPhoto.fromJson(Map<String, dynamic> json) {
    return PropertyPhoto(
      id: json['id'] as int,
      url: json['url'] as String,
      position: json['position'] as int? ?? 0,
    );
  }

  @override
  List<Object?> get props => [id, url, position];
}
