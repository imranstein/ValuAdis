import 'package:equatable/equatable.dart';

/// A rental application. The backend serves two shapes: the renter's own
/// applications (with property + band context) and the owner's inbox view (with
/// the applicant's name/phone). This model reads whichever fields are present.
class RentalApplication extends Equatable {
  const RentalApplication({
    required this.id,
    required this.status,
    required this.offeredRent,
    this.listingPublicId,
    this.listingStatus,
    this.propertyAddress,
    this.bandMin,
    this.bandMax,
    this.message,
    this.renterName,
    this.renterPhone,
    this.decidedAt,
    this.createdAt,
  });

  final int id;
  final String status;
  final double offeredRent;
  final String? listingPublicId;
  final String? listingStatus;
  final String? propertyAddress;
  final double? bandMin;
  final double? bandMax;
  final String? message;
  final String? renterName; // owner-inbox view only
  final String? renterPhone; // owner-inbox view only
  final DateTime? decidedAt;
  final DateTime? createdAt;

  bool get isPending => status.toLowerCase() == 'pending';

  factory RentalApplication.fromJson(Map<String, dynamic> json) {
    return RentalApplication(
      id: json['id'] as int,
      status: json['status'] as String? ?? 'pending',
      offeredRent: _d(json['offered_rent']) ?? 0,
      listingPublicId: json['listing_public_id'] as String?,
      listingStatus: json['listing_status'] as String?,
      propertyAddress: json['property_address'] as String?,
      bandMin: _d(json['band_min']),
      bandMax: _d(json['band_max']),
      message: json['message'] as String?,
      renterName: json['renter_name'] as String?,
      renterPhone: json['renter_phone'] as String?,
      decidedAt: _dt(json['decided_at']),
      createdAt: _dt(json['created_at']),
    );
  }

  @override
  List<Object?> get props => [id, status, offeredRent, decidedAt];
}

double? _d(dynamic v) => v == null
    ? null
    : (v is num ? v.toDouble() : double.tryParse(v.toString()));
DateTime? _dt(dynamic v) => v == null ? null : DateTime.tryParse(v.toString());
