import 'package:equatable/equatable.dart';

/// A registered tenancy contract, from GET /rentals/my-contracts. The contract
/// number is the human-quotable registry id (e.g. AA-RNT-2026-000123). PDF is
/// downloaded on demand via the contract endpoint.
class TenancyContract extends Equatable {
  const TenancyContract({
    required this.contractNo,
    required this.status,
    required this.monthlyRent,
    this.listingPublicId,
    this.startDate,
    this.endDate,
    this.depositAmount,
    this.depositReceiptRef,
    this.depositPaidOn,
    this.hasPdf = false,
    this.createdAt,
  });

  final String contractNo;
  final String status;
  final double monthlyRent;
  final String? listingPublicId;
  final DateTime? startDate;
  final DateTime? endDate;
  final double? depositAmount;
  final String? depositReceiptRef;
  final DateTime? depositPaidOn;
  final bool hasPdf;
  final DateTime? createdAt;

  bool get isActive => status.toLowerCase() == 'active';
  bool get depositRecorded =>
      depositReceiptRef != null && depositReceiptRef!.isNotEmpty;

  factory TenancyContract.fromJson(Map<String, dynamic> json) {
    return TenancyContract(
      contractNo: json['contract_no'] as String,
      status: json['status'] as String? ?? 'draft',
      monthlyRent: _d(json['monthly_rent']) ?? 0,
      listingPublicId: json['listing_public_id'] as String?,
      startDate: _dt(json['start_date']),
      endDate: _dt(json['end_date']),
      depositAmount: _d(json['deposit_amount']),
      depositReceiptRef: json['deposit_receipt_ref'] as String?,
      depositPaidOn: _dt(json['deposit_paid_on']),
      hasPdf: json['contract_pdf'] != null,
      createdAt: _dt(json['created_at']),
    );
  }

  @override
  List<Object?> get props => [contractNo, status, monthlyRent];
}

double? _d(dynamic v) => v == null
    ? null
    : (v is num ? v.toDouble() : double.tryParse(v.toString()));
DateTime? _dt(dynamic v) => v == null ? null : DateTime.tryParse(v.toString());
