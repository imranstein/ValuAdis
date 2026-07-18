import 'package:flutter_test/flutter_test.dart';
import 'package:valuadis_rent/data/models/session_user.dart';

void main() {
  group('SessionUser.typeFromRoles', () {
    test('property_owner role wins', () {
      expect(SessionUser.typeFromRoles(['renter', 'property_owner']),
          AccountType.propertyOwner);
    });

    test('renter role maps to renter', () {
      expect(SessionUser.typeFromRoles(['renter']), AccountType.renter);
    });

    test('rental_officer role maps to officer', () {
      expect(SessionUser.typeFromRoles(['rental_officer']),
          AccountType.officer);
    });

    test('no known role falls back to the provided fallback', () {
      expect(
        SessionUser.typeFromRoles([], fallback: AccountType.renter),
        AccountType.renter,
      );
    });
  });

  group('needsOwnerVerification', () {
    test('is true for an unverified owner', () {
      const user =
          SessionUser(accountType: AccountType.propertyOwner, ownerVerified: false);
      expect(user.needsOwnerVerification, isTrue);
    });

    test('is false once the owner is verified', () {
      const user =
          SessionUser(accountType: AccountType.propertyOwner, ownerVerified: true);
      expect(user.needsOwnerVerification, isFalse);
    });

    test('is false for a renter', () {
      const user = SessionUser(accountType: AccountType.renter);
      expect(user.needsOwnerVerification, isFalse);
    });
  });

  test('fromMeJson derives type from roles and Fayda id from license_number', () {
    final user = SessionUser.fromMeJson({
      'id': 7,
      'full_name': 'Test Owner',
      'email': 'owner@example.com',
      'roles': ['property_owner'],
      'owner_verified': false,
      'license_number': 'FAYDA-123456',
      'municipality': 'Bole',
    });
    expect(user.accountType, AccountType.propertyOwner);
    expect(user.faydaId, '123456');
    expect(user.ownerVerified, isFalse);
    expect(user.municipality, 'Bole');
  });
}
