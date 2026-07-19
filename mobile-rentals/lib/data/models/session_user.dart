import 'package:equatable/equatable.dart';

enum AccountType { renter, propertyOwner, officer, unknown }

/// The signed-in citizen. account_type comes from signup; the richer profile
/// (name, Fayda id, phone, owner verification) comes from /auth/me.
class SessionUser extends Equatable {
  const SessionUser({
    required this.accountType,
    this.id,
    this.fullName,
    this.email,
    this.phone,
    this.faydaId,
    this.municipality,
    this.ownerVerified = false,
  });

  final AccountType accountType;
  final int? id;
  final String? fullName;
  final String? email;
  final String? phone;
  final String? faydaId;
  final String? municipality;
  final bool ownerVerified;

  bool get isOwner => accountType == AccountType.propertyOwner;
  bool get isRenter => accountType == AccountType.renter;

  /// Owners must be verified by a rental officer before a listing can publish.
  bool get needsOwnerVerification => isOwner && !ownerVerified;

  static AccountType typeFromString(String? raw) {
    switch (raw) {
      case 'property_owner':
        return AccountType.propertyOwner;
      case 'renter':
        return AccountType.renter;
      case 'rental_officer':
        return AccountType.officer;
      default:
        return AccountType.unknown;
    }
  }

  SessionUser copyWith({
    AccountType? accountType,
    int? id,
    String? fullName,
    String? email,
    String? phone,
    String? faydaId,
    String? municipality,
    bool? ownerVerified,
  }) {
    return SessionUser(
      accountType: accountType ?? this.accountType,
      id: id ?? this.id,
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      faydaId: faydaId ?? this.faydaId,
      municipality: municipality ?? this.municipality,
      ownerVerified: ownerVerified ?? this.ownerVerified,
    );
  }

  factory SessionUser.fromMeJson(
    Map<String, dynamic> json, {
    AccountType fallbackType = AccountType.unknown,
  }) {
    final roles = (json['roles'] as List?)?.map((e) => e.toString()).toList() ??
        const <String>[];
    return SessionUser(
      accountType: typeFromRoles(roles, fallback: fallbackType),
      id: json['id'] as int?,
      fullName: json['full_name'] as String?,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      // Citizens carry their Fayda id inside license_number as "FAYDA-<id>".
      faydaId: _faydaFromLicense(json['license_number'] as String?),
      municipality: json['municipality'] as String?,
      ownerVerified: json['owner_verified'] as bool? ?? false,
    );
  }

  static AccountType typeFromRoles(
    List<String> roles, {
    AccountType fallback = AccountType.unknown,
  }) {
    if (roles.contains('property_owner')) return AccountType.propertyOwner;
    if (roles.contains('renter')) return AccountType.renter;
    if (roles.contains('rental_officer')) return AccountType.officer;
    return fallback;
  }

  static String? _faydaFromLicense(String? license) {
    if (license == null) return null;
    return license.startsWith('FAYDA-') ? license.substring(6) : null;
  }

  @override
  List<Object?> get props =>
      [accountType, id, email, faydaId, ownerVerified];
}
