import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'app.dart';
import 'blocs/auth/auth_bloc.dart';
import 'core/locale_controller.dart';
import 'data/api/api_client.dart';
import 'data/api/token_storage.dart';
import 'data/repositories/auth_repository.dart';
import 'data/repositories/rentals_repository.dart';

void main() {
  runZonedGuarded<Future<void>>(() async {
    WidgetsFlutterBinding.ensureInitialized();

    FlutterError.onError = (details) {
      FlutterError.presentError(details);
      _reportError(details.exception, details.stack);
    };
    PlatformDispatcher.instance.onError = (error, stack) {
      _reportError(error, stack);
      return true;
    };

    final storage = TokenStorage();
    late final AuthBloc authBloc;
    // A 401 that survives one refresh forces a clean re-login through the bloc.
    final apiClient = ApiClient(
      storage,
      onUnauthorized: () => authBloc.add(const AuthSessionExpired()),
    );
    final authRepository = AuthRepository(apiClient, storage);
    authBloc = AuthBloc(authRepository)..add(const AuthCheckRequested());
    final rentalsRepository = RentalsRepository(apiClient);
    final localeController = LocaleController();

    runApp(ValuAdisRentApp(
      authBloc: authBloc,
      rentalsRepository: rentalsRepository,
      localeController: localeController,
    ));
  }, _reportError);
}

// Crash-reporting hook point. Until a DSN is wired, errors are logged so release
// failures are not silently swallowed.
void _reportError(Object error, StackTrace? stack) {
  debugPrint('Unhandled error: $error');
  if (stack != null) debugPrint('$stack');
}
