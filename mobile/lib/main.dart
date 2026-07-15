import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'data/datasources/local/database_helper.dart';
import 'data/datasources/local/hive_helper.dart';
import 'presentation/app.dart';

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

    await HiveHelper.init();
    await DatabaseHelper.instance.database;
    runApp(const ValuAdisApp());
  }, _reportError);
}

// NOTE: crash-reporting hook point. When a Sentry/Crashlytics DSN exists,
// forward errors from here; until then they are logged so release failures
// are not silently swallowed.
void _reportError(Object error, StackTrace? stack) {
  debugPrint('Unhandled error: $error');
  if (stack != null) {
    debugPrint('$stack');
  }
}
