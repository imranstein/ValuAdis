import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_typography.dart';

/// Builds [ThemeData] for a given [AppColors] set. Widgets mostly read
/// [AppColors] directly for semantic roles; this theme covers Material
/// defaults (ripples, selection, scaffold background) so nothing leaks the
/// stock blue/white.
class AppTheme {
  AppTheme._();

  static ThemeData build(AppColors c) {
    final base = c.isDark ? ThemeData.dark() : ThemeData.light();
    return base.copyWith(
      scaffoldBackgroundColor: c.canvas,
      canvasColor: c.canvas,
      splashFactory: InkRipple.splashFactory,
      colorScheme: (c.isDark
              ? const ColorScheme.dark()
              : const ColorScheme.light())
          .copyWith(
        primary: c.green,
        onPrimary: c.onGreen,
        secondary: c.gold,
        surface: c.surface,
        onSurface: c.ink,
        error: c.danger,
        brightness: c.isDark ? Brightness.dark : Brightness.light,
      ),
      textTheme: AppType.bodyTextTheme(c.ink, c.inkSecondary),
      dividerColor: c.border,
      iconTheme: IconThemeData(color: c.inkSecondary),
      appBarTheme: AppBarTheme(
        backgroundColor: c.canvas,
        surfaceTintColor: Colors.transparent,
        foregroundColor: c.ink,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: AppType.headline(c),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: c.surface,
        surfaceTintColor: Colors.transparent,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: c.isDark ? c.surfaceSunken : c.ink,
        contentTextStyle: AppType.body(c, color: c.isDark ? c.ink : c.onGreen),
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}
