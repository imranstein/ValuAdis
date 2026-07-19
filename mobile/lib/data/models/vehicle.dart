import 'package:equatable/equatable.dart';

/// Mirrors the backend `VehicleResponse` schema
/// (`backend/app/modules/vehicle/schemas.py`).
class Vehicle extends Equatable {
  final int id;
  final int userId;
  final String make;
  final String model;
  final int year;
  final String vin;
  final String plateNumber;
  final String? bodyType;
  final String? fuelType;
  final String? transmission;
  final int? engineCapacity;
  final int? mileage;
  final String? color;
  final int previousOwners;
  final double? purchasePrice;
  final String? region;
  final String? city;
  final int? importYear;
  final bool customDutyPaid;
  final String? description;
  final String? notes;
  final bool isActive;
  final bool isListedForSale;
  final String createdAt;
  final String updatedAt;

  const Vehicle({
    required this.id,
    required this.userId,
    required this.make,
    required this.model,
    required this.year,
    required this.vin,
    required this.plateNumber,
    this.bodyType,
    this.fuelType,
    this.transmission,
    this.engineCapacity,
    this.mileage,
    this.color,
    this.previousOwners = 1,
    this.purchasePrice,
    this.region,
    this.city,
    this.importYear,
    this.customDutyPaid = false,
    this.description,
    this.notes,
    this.isActive = true,
    this.isListedForSale = false,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Vehicle.fromJson(Map<String, dynamic> json) {
    return Vehicle(
      id: json['id'] as int,
      userId: json['user_id'] as int? ?? 0,
      make: json['make'] as String? ?? '',
      model: json['model'] as String? ?? '',
      year: json['year'] as int? ?? 0,
      vin: json['vin'] as String? ?? '',
      plateNumber: json['plate_number'] as String? ?? '',
      bodyType: json['body_type'] as String?,
      fuelType: json['fuel_type'] as String?,
      transmission: json['transmission'] as String?,
      engineCapacity: json['engine_capacity'] as int?,
      mileage: json['mileage'] as int?,
      color: json['color'] as String?,
      previousOwners: json['previous_owners'] as int? ?? 1,
      purchasePrice: (json['purchase_price'] as num?)?.toDouble(),
      region: json['region'] as String?,
      city: json['city'] as String?,
      importYear: json['import_year'] as int?,
      customDutyPaid: json['custom_duty_paid'] as bool? ?? false,
      description: json['description'] as String?,
      notes: json['notes'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      isListedForSale: json['is_listed_for_sale'] as bool? ?? false,
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }

  String get displayName => '$make $model ($year)';

  @override
  List<Object?> get props => [
        id,
        userId,
        make,
        model,
        year,
        vin,
        plateNumber,
        bodyType,
        fuelType,
        transmission,
        engineCapacity,
        mileage,
        color,
        previousOwners,
        purchasePrice,
        region,
        city,
        importYear,
        customDutyPaid,
        description,
        notes,
        isActive,
        isListedForSale,
        createdAt,
        updatedAt,
      ];
}
