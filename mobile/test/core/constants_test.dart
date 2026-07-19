import 'package:flutter_test/flutter_test.dart';

import 'package:valuadis/core/constants.dart';

void main() {
  group('resolveApiBaseUrl', () {
    test('falls back to localhost in non-release builds', () {
      expect(
        AppConstants.resolveApiBaseUrl('', false),
        'http://localhost:8000',
      );
    });

    test('returns the defined URL in release builds', () {
      expect(
        AppConstants.resolveApiBaseUrl('https://api.valuadis.com', true),
        'https://api.valuadis.com',
      );
    });

    test('throws when release build has no API_BASE_URL', () {
      expect(
        () => AppConstants.resolveApiBaseUrl('', true),
        throwsStateError,
      );
    });

    test('throws when release build points at localhost', () {
      expect(
        () => AppConstants.resolveApiBaseUrl('http://localhost:8000', true),
        throwsStateError,
      );
    });

    test('throws when release build points at the Android emulator host', () {
      expect(
        () => AppConstants.resolveApiBaseUrl('http://10.0.2.2:8000', true),
        throwsStateError,
      );
    });
  });
}
