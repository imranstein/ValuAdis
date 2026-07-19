import 'package:equatable/equatable.dart';

/// Request payload for `POST /api/v1/valuations/quick`.
///
/// Field names and allowed values mirror the backend valuation service
/// (`backend/app/modules/valuation/services.py`). `municipality` and
/// `areaSqm` are required; the remaining fields fall back to backend
/// defaults when omitted.
class QuickValuationRequest extends Equatable {
  final String municipality;
  final double areaSqm;
  final String propertyType;
  final String condition;
  final String neighborhoodQuality;

  const QuickValuationRequest({
    required this.municipality,
    required this.areaSqm,
    this.propertyType = 'residential',
    this.condition = 'good',
    this.neighborhoodQuality = 'average',
  });

  Map<String, dynamic> toJson() {
    return {
      'municipality': municipality,
      'area_sqm': areaSqm,
      'property_type': propertyType,
      'condition': condition,
      'neighborhood_quality': neighborhoodQuality,
    };
  }

  @override
  List<Object?> get props => [
        municipality,
        areaSqm,
        propertyType,
        condition,
        neighborhoodQuality,
      ];
}

/// Result of a quick valuation, mirroring the backend `ValuationCalculation`
/// response schema.
class QuickValuationResult extends Equatable {
  final double marketValue;
  final double taxableValue;
  final double baseRate;
  final double multiplier;

  const QuickValuationResult({
    required this.marketValue,
    required this.taxableValue,
    required this.baseRate,
    required this.multiplier,
  });

  factory QuickValuationResult.fromJson(Map<String, dynamic> json) {
    return QuickValuationResult(
      marketValue: (json['market_value'] as num?)?.toDouble() ?? 0,
      taxableValue: (json['taxable_value'] as num?)?.toDouble() ?? 0,
      baseRate: (json['base_rate'] as num?)?.toDouble() ?? 0,
      multiplier: (json['multiplier'] as num?)?.toDouble() ?? 0,
    );
  }

  @override
  List<Object?> get props => [marketValue, taxableValue, baseRate, multiplier];
}
