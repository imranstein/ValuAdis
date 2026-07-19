import 'package:equatable/equatable.dart';

import 'band.dart';

/// Property facts safe for the public listing surface (mirrors the backend's
/// closed PublicListingProperty model — no ownership PII exists here by design).
class ListingProperty extends Equatable {
  const ListingProperty({
    required this.address,
    required this.municipality,
    this.subcity,
    required this.propertyType,
    this.propertySubtype,
    required this.areaSqm,
    this.buildingAreaSqm,
    this.bedrooms,
    this.bathrooms,
    this.floors,
    this.yearBuilt,
    this.condition,
    this.latitude,
    this.longitude,
    this.photoUrls = const [],
  });

  final String address;
  final String municipality;
  final String? subcity;
  final String propertyType;
  final String? propertySubtype;
  final double areaSqm;
  final double? buildingAreaSqm;
  final int? bedrooms;
  final int? bathrooms;
  final int? floors;
  final int? yearBuilt;
  final String? condition;
  final double? latitude;
  final double? longitude;
  final List<String> photoUrls;

  bool get hasLocation => latitude != null && longitude != null;
  bool get hasPhotos => photoUrls.isNotEmpty;

  factory ListingProperty.fromJson(Map<String, dynamic> json) {
    return ListingProperty(
      address: json['address'] as String? ?? 'Unknown address',
      municipality: json['municipality'] as String? ?? '',
      subcity: json['subcity'] as String?,
      propertyType: json['property_type'] as String? ?? 'residential',
      propertySubtype: json['property_subtype'] as String?,
      areaSqm: _toDouble(json['area_sqm']) ?? 0,
      buildingAreaSqm: _toDouble(json['building_area_sqm']),
      bedrooms: json['number_of_bedrooms'] as int?,
      bathrooms: json['number_of_bathrooms'] as int?,
      floors: json['number_of_floors'] as int?,
      yearBuilt: json['year_built'] as int?,
      condition: json['condition'] as String?,
      latitude: _toDouble(json['latitude']),
      longitude: _toDouble(json['longitude']),
      photoUrls: (json['photo_urls'] as List?)?.whereType<String>().toList() ??
          const [],
    );
  }

  @override
  List<Object?> get props =>
      [address, municipality, subcity, areaSqm, bedrooms, photoUrls];
}

/// A published listing as an anonymous renter sees it. Owner identity and
/// internal ids are never fields here (enforced server-side).
class Listing extends Equatable {
  const Listing({
    required this.publicId,
    required this.band,
    required this.hasCertificate,
    required this.property,
    this.publishedAt,
  });

  final String publicId;
  final RentBand band;
  final bool hasCertificate;
  final ListingProperty property;
  final DateTime? publishedAt;

  factory Listing.fromJson(Map<String, dynamic> json) {
    return Listing(
      publicId: json['public_id'] as String,
      band: RentBand(
        min: _toDouble(json['band_min']) ?? 0,
        max: _toDouble(json['band_max']) ?? 0,
        suggested: _toDouble(json['suggested_rent']) ?? 0,
      ),
      hasCertificate: json['has_valuation_certificate'] as bool? ?? false,
      property:
          ListingProperty.fromJson(json['property'] as Map<String, dynamic>),
      publishedAt: _toDate(json['published_at']),
    );
  }

  @override
  List<Object?> get props => [publicId, band, hasCertificate];
}

double? _toDouble(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString());
}

DateTime? _toDate(dynamic v) {
  if (v == null) return null;
  return DateTime.tryParse(v.toString());
}
