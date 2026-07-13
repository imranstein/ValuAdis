import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Civic-ledger palette — aligned with the web app (deep forest green +
  // warm gold accent, warm paper surfaces). No blue.
  static const primary = Color(0xFF235C43);
  static const primaryLight = Color(0xFF3D7D5D);
  static const primaryDark = Color(0xFF163C2B);
  static const secondary = Color(0xFF8A5F14); // warm gold (was blue)
  static const surface = Color(0xFFFCFAF3);
  static const background = Color(0xFFF6F3EA);
  static const outline = Color(0xFFC2BBA4);
  static const error = Color(0xFF9D3A28);
  static const success = Color(0xFF235C43);
  static const textPrimary = Color(0xFF1B231D);
  static const onSurface = Color(0xFF1B231D);
  static const surfaceText = Color(0xFF39443B);
  static const white = Color(0xFFFFFFFF);
}

class AppSpacing {
  AppSpacing._();

  static const double page = 24;
  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 20;
  static const double xl = 24;
  static const double xxl = 32;
  static const double radiusSm = 10;
  static const double radiusMd = 14;
}

class AppRadius {
  AppRadius._();

  static const Radius md = Radius.circular(AppSpacing.radiusMd);
  static const BorderRadius mdRadius = BorderRadius.all(md);
  static const Radius sm = Radius.circular(AppSpacing.radiusSm);
  static const BorderRadius smRadius = BorderRadius.all(sm);
}

class AppTypo {
  AppTypo._();

  static const String fontFamily = 'Inter';

  static TextTheme textTheme() => const TextTheme(
    headlineSmall: TextStyle(
      fontWeight: FontWeight.w700,
      fontSize: 30,
      height: 1.2,
      letterSpacing: 0,
      fontFamily: fontFamily,
    ),
    titleLarge: TextStyle(
      fontWeight: FontWeight.w600,
      fontSize: 20,
      height: 1.3,
      letterSpacing: 0.1,
      fontFamily: fontFamily,
    ),
    titleMedium: TextStyle(
      fontWeight: FontWeight.w600,
      fontSize: 16,
      letterSpacing: 0.1,
      fontFamily: fontFamily,
    ),
    bodyLarge: TextStyle(fontSize: 16, height: 1.4, fontFamily: fontFamily),
    bodyMedium: TextStyle(fontSize: 14, height: 1.4, fontFamily: fontFamily),
    bodySmall: TextStyle(fontSize: 12, height: 1.3, fontFamily: fontFamily),
  );
}

class AppTheme {
  AppTheme._();

  static ThemeData build() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: Brightness.light,
      primary: AppColors.primary,
      onPrimary: Colors.white,
      secondary: AppColors.secondary,
      surface: AppColors.surface,
      error: AppColors.error,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: AppColors.background,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.surface,
        foregroundColor: colorScheme.onSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surface,
        border: OutlineInputBorder(
          borderRadius: AppRadius.mdRadius,
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdRadius,
          borderSide: BorderSide(color: AppColors.outline.withOpacity(0.4)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdRadius,
          borderSide: const BorderSide(color: AppColors.primary, width: 1.2),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: AppColors.white,
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.lg,
            vertical: AppSpacing.sm,
          ),
          shape: RoundedRectangleBorder(borderRadius: AppRadius.mdRadius),
          minimumSize: const Size.fromHeight(48),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 16,
            letterSpacing: 0.1,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.lg,
            vertical: AppSpacing.sm,
          ),
          shape: RoundedRectangleBorder(borderRadius: AppRadius.mdRadius),
          minimumSize: const Size.fromHeight(48),
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: AppColors.surface,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdRadius),
        margin: const EdgeInsets.only(bottom: AppSpacing.sm),
      ),
      textTheme: AppTypo.textTheme(),
    );
  }
}
