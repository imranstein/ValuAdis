import 'package:equatable/equatable.dart';

/// One published district/subtype/bedrooms median for a period. Rows below the
/// backend's small-sample suppression threshold never reach the client, so a
/// district that shows nothing genuinely has no publishable data.
class RentIndexRow extends Equatable {
  const RentIndexRow({
    required this.district,
    required this.propertySubtype,
    required this.medianRent,
    required this.sampleSize,
    required this.source,
    required this.period,
    this.bedrooms,
  });

  final String district;
  final String propertySubtype;
  final double medianRent;
  final int sampleSize;
  final String source;
  final String period;
  final int? bedrooms;

  factory RentIndexRow.fromJson(Map<String, dynamic> json) {
    return RentIndexRow(
      district: json['district'] as String? ?? '',
      propertySubtype: json['property_subtype'] as String? ?? '',
      medianRent: (json['median_rent'] as num?)?.toDouble() ?? 0,
      sampleSize: json['sample_size'] as int? ?? 0,
      source: json['source'] as String? ?? '',
      period: json['period'] as String? ?? '',
      bedrooms: json['bedrooms'] as int?,
    );
  }

  @override
  List<Object?> get props =>
      [district, propertySubtype, bedrooms, medianRent, period];
}
