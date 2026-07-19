import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'blocs/auth/auth_bloc.dart';
import 'core/constants.dart';
import 'core/locale_controller.dart';
import 'core/theme/app_colors.dart';
import 'core/theme/app_theme.dart';
import 'data/repositories/rentals_repository.dart';
import 'l10n/app_localizations.dart';
import 'ui/screens/auth/auth_flow.dart';
import 'ui/screens/home_shell.dart';
import 'ui/screens/splash_screen.dart';

/// App root. Provides the [AuthBloc], [RentalsRepository], and
/// [LocaleController] to the tree, sets up the light/dark themes, and gates
/// between the auth flow and the home shell on session state.
class ValuAdisRentApp extends StatelessWidget {
  const ValuAdisRentApp({
    super.key,
    required this.authBloc,
    required this.rentalsRepository,
    required this.localeController,
  });

  final AuthBloc authBloc;
  final RentalsRepository rentalsRepository;
  final LocaleController localeController;

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider.value(value: rentalsRepository),
        RepositoryProvider.value(value: localeController),
      ],
      child: BlocProvider.value(
        value: authBloc,
        child: ValueListenableBuilder<Locale?>(
          valueListenable: localeController.locale,
          builder: (context, locale, _) => MaterialApp(
            title: AppConstants.appName,
            debugShowCheckedModeBanner: false,
            theme: AppTheme.build(AppColors.light),
            darkTheme: AppTheme.build(AppColors.dark),
            themeMode: ThemeMode.system,
            locale: locale,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            builder: (context, child) {
              final isDark = Theme.of(context).brightness == Brightness.dark;
              return AppColorsScope(
                colors: isDark ? AppColors.dark : AppColors.light,
                child: child ?? const SizedBox.shrink(),
              );
            },
            home: const _AuthGate(),
          ),
        ),
      ),
    );
  }
}

class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        switch (state.status) {
          case AuthStatus.unknown:
            return const SplashScreen();
          case AuthStatus.authenticated:
            return HomeShell(user: state.user!);
          case AuthStatus.authenticating:
          case AuthStatus.unauthenticated:
          case AuthStatus.failure:
            return const AuthFlow();
        }
      },
    );
  }
}
