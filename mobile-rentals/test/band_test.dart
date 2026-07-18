import 'package:flutter_test/flutter_test.dart';
import 'package:valuadis_rent/data/models/band.dart';

void main() {
  const band = RentBand(min: 25200, max: 30800, suggested: 28000);

  group('RentBand.contains', () {
    test('returns true for a value inside the band', () {
      expect(band.contains(27500), isTrue);
    });

    test('returns true at the exact bounds', () {
      expect(band.contains(25200), isTrue);
      expect(band.contains(30800), isTrue);
    });

    test('returns false below the band', () {
      expect(band.contains(25000), isFalse);
    });

    test('returns false above the band', () {
      expect(band.contains(31000), isFalse);
    });
  });

  group('RentBand.clamp', () {
    test('leaves an in-band value unchanged', () {
      expect(band.clamp(27000), 27000);
    });

    test('raises a below-band value to the minimum', () {
      expect(band.clamp(10000), 25200);
    });

    test('lowers an above-band value to the maximum', () {
      expect(band.clamp(99000), 30800);
    });

    test('collapses to the minimum when the band has no width', () {
      const flat = RentBand(min: 20000, max: 20000, suggested: 20000);
      expect(flat.clamp(50000), 20000);
    });
  });

  group('RentBand.positionOf', () {
    test('maps the minimum to 0', () {
      expect(band.positionOf(25200), 0);
    });

    test('maps the maximum to 1', () {
      expect(band.positionOf(30800), 1);
    });

    test('maps the midpoint to 0.5', () {
      expect(band.positionOf(28000), closeTo(0.5, 0.0001));
    });

    test('clamps an out-of-band value to the range', () {
      expect(band.positionOf(40000), 1);
      expect(band.positionOf(0), 0);
    });
  });

  test('spreadPercent reflects the +/-10% headroom', () {
    expect(band.spreadPercent, 10);
  });
}
