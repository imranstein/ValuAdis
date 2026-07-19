import 'package:flutter/animation.dart';

/// Motion tokens. Strong ease-out curves only (no bounce/elastic), UI motion
/// kept under 400ms. See DESIGN.md section 6.
class Motion {
  Motion._();

  // Strong ease-out variants — the built-in curves are too weak.
  static const Cubic easeOutQuart = Cubic(0.25, 1, 0.5, 1);
  static const Cubic easeOutQuint = Cubic(0.22, 1, 0.36, 1);
  static const Cubic easeOutExpo = Cubic(0.16, 1, 0.3, 1);
  static const Cubic easeInOut = Cubic(0.77, 0, 0.175, 1);

  static const Duration press = Duration(milliseconds: 120);
  static const Duration feedback = Duration(milliseconds: 160);
  static const Duration sheet = Duration(milliseconds: 280);
  static const Duration hero = Duration(milliseconds: 360);
  static const Duration nav = Duration(milliseconds: 240);

  /// Per-item stagger delay for list reveals, capped so long lists never lag.
  static Duration staggerFor(int index) =>
      Duration(milliseconds: (index.clamp(0, 8)) * 45);
}
