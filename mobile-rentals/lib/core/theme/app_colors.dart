import 'package:flutter/material.dart';

/// Civic-ledger palette adapted for consumer mobile. Neutrals are tinted toward
/// the brand green; no pure black or white. Derived from
/// frontend/design-tokens.json. See DESIGN.md section 2.
///
/// A single [AppColors] instance is resolved per brightness and handed down the
/// tree via [AppColorsScope], so widgets read semantic roles, never raw hex.
@immutable
class AppColors {
  const AppColors({
    required this.canvas,
    required this.surface,
    required this.surfaceSunken,
    required this.ink,
    required this.inkSecondary,
    required this.inkMuted,
    required this.border,
    required this.borderStrong,
    required this.green,
    required this.greenDeep,
    required this.greenLight,
    required this.greenSoft,
    required this.gold,
    required this.goldWash,
    required this.onGreen,
    required this.danger,
    required this.dangerWash,
    required this.isDark,
  });

  final Color canvas;
  final Color surface;
  final Color surfaceSunken;
  final Color ink;
  final Color inkSecondary;
  final Color inkMuted;
  final Color border;
  final Color borderStrong;
  final Color green;
  final Color greenDeep;
  final Color greenLight;
  final Color greenSoft;
  final Color gold;
  final Color goldWash;
  final Color onGreen;
  final Color danger;
  final Color dangerWash;
  final bool isDark;

  static const AppColors light = AppColors(
    canvas: Color(0xFFF6F3EA),
    surface: Color(0xFFFCFAF3),
    surfaceSunken: Color(0xFFEEEADD),
    ink: Color(0xFF1B231D),
    inkSecondary: Color(0xFF39443B),
    inkMuted: Color(0xFF5C665D),
    border: Color(0xFFDED8C6),
    borderStrong: Color(0xFFC2BBA4),
    green: Color(0xFF235C43),
    greenDeep: Color(0xFF163C2B),
    greenLight: Color(0xFF5C8A70),
    greenSoft: Color(0xFFDFE8DD),
    gold: Color(0xFF8A5F14),
    goldWash: Color(0xFFFAF4E4),
    onGreen: Color(0xFFF4F1E6),
    danger: Color(0xFF9B2F2F),
    dangerWash: Color(0xFFF3E2E0),
    isDark: false,
  );

  static const AppColors dark = AppColors(
    canvas: Color(0xFF101A14),
    surface: Color(0xFF16241B),
    surfaceSunken: Color(0xFF1C2B21),
    ink: Color(0xFFF1EEE0),
    inkSecondary: Color(0xFFC3CFC5),
    inkMuted: Color(0xFF9DB0A0),
    border: Color(0xFF26382C),
    borderStrong: Color(0xFF31473A),
    green: Color(0xFF5C8A70),
    greenDeep: Color(0xFF3E6B52),
    greenLight: Color(0xFF7CA98E),
    greenSoft: Color(0xFF23392C),
    gold: Color(0xFFD3A94C),
    goldWash: Color(0xFF2A2416),
    onGreen: Color(0xFF0E1A12),
    danger: Color(0xFFE08A8A),
    dangerWash: Color(0xFF32211F),
    isDark: true,
  );

  static AppColors of(BuildContext context) => AppColorsScope.of(context);
}

class AppColorsScope extends InheritedWidget {
  const AppColorsScope({super.key, required this.colors, required super.child});

  final AppColors colors;

  static AppColors of(BuildContext context) {
    final scope =
        context.dependOnInheritedWidgetOfExactType<AppColorsScope>();
    assert(scope != null, 'AppColorsScope missing from the widget tree');
    return scope!.colors;
  }

  @override
  bool updateShouldNotify(AppColorsScope oldWidget) =>
      colors.isDark != oldWidget.colors.isDark;
}
