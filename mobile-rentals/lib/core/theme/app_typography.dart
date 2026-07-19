import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';

/// Type roles per DESIGN.md section 3.
/// - Serif (Cormorant Garamond): brand/display moments only.
/// - Body (DM Sans): all functional UI.
/// - Mono (JetBrains Mono): ledger figures (ETB, band bounds, contract/Fayda ids).
///
/// google_fonts caches at runtime and degrades to a system fallback offline, so
/// no font files are bundled and the app still renders when the network is down.
class AppType {
  AppType._();

  static TextTheme bodyTextTheme(Color ink, Color secondary) {
    return GoogleFonts.dmSansTextTheme().apply(
      bodyColor: ink,
      displayColor: ink,
    ).copyWith(
      bodyMedium: GoogleFonts.dmSans(
        fontSize: 15,
        height: 1.45,
        color: secondary,
      ),
      labelLarge: GoogleFonts.dmSans(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.1,
      ),
    );
  }

  static TextStyle serifDisplay(
    AppColors c, {
    double size = 34,
    FontWeight weight = FontWeight.w600,
    Color? color,
  }) =>
      GoogleFonts.cormorantGaramond(
        fontSize: size,
        height: 1.08,
        fontWeight: weight,
        letterSpacing: -0.5,
        color: color ?? c.ink,
      );

  static TextStyle mono(
    AppColors c, {
    double size = 15,
    FontWeight weight = FontWeight.w600,
    Color? color,
    double letterSpacing = 0,
  }) =>
      GoogleFonts.jetBrainsMono(
        fontSize: size,
        fontWeight: weight,
        letterSpacing: letterSpacing,
        color: color ?? c.ink,
      );

  static TextStyle title(AppColors c) => GoogleFonts.dmSans(
        fontSize: 22,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.3,
        color: c.ink,
      );

  static TextStyle headline(AppColors c) => GoogleFonts.dmSans(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.2,
        color: c.ink,
      );

  static TextStyle body(AppColors c, {Color? color}) => GoogleFonts.dmSans(
        fontSize: 15,
        height: 1.45,
        color: color ?? c.inkSecondary,
      );

  static TextStyle label(AppColors c, {Color? color, FontWeight? weight}) =>
      GoogleFonts.dmSans(
        fontSize: 13,
        fontWeight: weight ?? FontWeight.w500,
        color: color ?? c.inkMuted,
      );

  static TextStyle caption(AppColors c, {Color? color}) => GoogleFonts.dmSans(
        fontSize: 11,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.3,
        color: color ?? c.inkMuted,
      );
}
