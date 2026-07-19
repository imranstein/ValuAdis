import 'package:flutter_test/flutter_test.dart';
import 'package:valuadis_rent/data/models/registry_status.dart';

void main() {
  group('application status mapping', () {
    test('pending maps to the pending kind', () {
      expect(RegistryStatus.kindOf('pending'), StatusKind.pending);
    });

    test('accepted maps to the positive kind', () {
      expect(RegistryStatus.kindOf('accepted'), StatusKind.positive);
    });

    test('rejected maps to the negative kind', () {
      expect(RegistryStatus.kindOf('rejected'), StatusKind.negative);
    });

    test('withdrawn maps to the neutral kind', () {
      expect(RegistryStatus.kindOf('withdrawn'), StatusKind.neutral);
    });
  });

  group('listing status mapping', () {
    test('published maps to positive', () {
      expect(RegistryStatus.kindOf('published'), StatusKind.positive);
    });

    test('pending_review maps to pending', () {
      expect(RegistryStatus.kindOf('pending_review'), StatusKind.pending);
    });
  });

  group('contract status mapping', () {
    test('active maps to positive', () {
      expect(RegistryStatus.kindOf('active'), StatusKind.positive);
    });

    test('terminated maps to negative', () {
      expect(RegistryStatus.kindOf('terminated'), StatusKind.negative);
    });
  });

  group('labels', () {
    test('rejected reads as a humane "Not selected"', () {
      expect(RegistryStatus.labelOf('rejected'), 'Not selected');
    });

    test('pending_review reads as "Under review"', () {
      expect(RegistryStatus.labelOf('pending_review'), 'Under review');
    });

    test('an unknown status falls back to a title-cased label', () {
      expect(RegistryStatus.labelOf('some_new_state'), 'Some new state');
    });

    test('a null status is labelled Unknown', () {
      expect(RegistryStatus.labelOf(null), 'Unknown');
    });
  });

  test('an unknown status is treated as neutral, never crashing', () {
    expect(RegistryStatus.kindOf('mystery'), StatusKind.neutral);
  });
}
