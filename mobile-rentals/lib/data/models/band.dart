import 'package:equatable/equatable.dart';

/// The published price band for a listing. The server is the source of truth and
/// re-validates every offer, but the client clamps and validates locally so the
/// apply slider can give instant, honest feedback (matching the server's rule).
class RentBand extends Equatable {
  const RentBand({
    required this.min,
    required this.max,
    required this.suggested,
  });

  final double min;
  final double max;
  final double suggested;

  /// True when [value] is inside the inclusive band. Mirrors the server's
  /// BandViolationError boundary (out-of-band offers are a 422).
  bool contains(num value) => value >= min && value <= max;

  /// Clamps an arbitrary input into the band. Used to keep the slider handle
  /// from ever proposing an offer the server would reject.
  double clamp(num value) {
    if (max <= min) return min.toDouble();
    return value.clamp(min, max).toDouble();
  }

  /// Position of [value] within the band as 0..1, for the visual range bar.
  /// Values outside the band are clamped to the ends rather than overflowing.
  double positionOf(num value) {
    if (max <= min) return 0;
    final ratio = (value - min) / (max - min);
    return ratio.clamp(0.0, 1.0).toDouble();
  }

  double get suggestedPosition => positionOf(suggested);

  /// Half-width of the band as a percentage of the suggested rent (the plan's
  /// +/-10% headroom), for honest "within N%" copy.
  int get spreadPercent {
    if (suggested <= 0) return 0;
    return (((max - min) / 2) / suggested * 100).round();
  }

  @override
  List<Object?> get props => [min, max, suggested];
}
