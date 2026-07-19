import 'package:equatable/equatable.dart';

import 'band.dart';

/// An owner's own listing (any status), from GET /rentals/my-listings.
/// Unlike the public [Listing], this carries the review state the owner needs:
/// status, whether officer review is required, and the review reason.
class OwnerListing extends Equatable {
  const OwnerListing({
    required this.publicId,
    required this.propertyId,
    required this.status,
    required this.band,
    this.propertyAddress,
    this.requiresOfficerReview = false,
    this.reviewReason,
    this.hasAgreement = false,
    this.publishedAt,
    this.createdAt,
  });

  final String publicId;
  final int propertyId;
  final String status;
  final RentBand band;
  final String? propertyAddress;
  final bool requiresOfficerReview;
  final String? reviewReason;
  final bool hasAgreement;
  final DateTime? publishedAt;
  final DateTime? createdAt;

  bool get isPublished => status.toLowerCase() == 'published';

  factory OwnerListing.fromJson(Map<String, dynamic> json) {
    return OwnerListing(
      publicId: json['public_id'] as String,
      propertyId: json['property_id'] as int? ?? 0,
      status: json['status'] as String? ?? 'draft',
      band: RentBand(
        min: _d(json['band_min']) ?? 0,
        max: _d(json['band_max']) ?? 0,
        suggested: _d(json['suggested_rent']) ?? 0,
      ),
      propertyAddress: json['property_address'] as String?,
      requiresOfficerReview: json['requires_officer_review'] as bool? ?? false,
      reviewReason: json['review_reason'] as String?,
      hasAgreement: json['listing_agreement_pdf'] != null,
      publishedAt: _dt(json['published_at']),
      createdAt: _dt(json['created_at']),
    );
  }

  @override
  List<Object?> get props => [publicId, status, band];
}

double? _d(dynamic v) => v == null
    ? null
    : (v is num ? v.toDouble() : double.tryParse(v.toString()));
DateTime? _dt(dynamic v) => v == null ? null : DateTime.tryParse(v.toString());
