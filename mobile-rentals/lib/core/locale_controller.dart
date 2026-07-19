import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Persists the citizen's language choice. `null` means "follow the system
/// locale" (the default on first launch); an explicit [Locale] means the user
/// overrode it from Profile. Mirrors [TokenStorage]'s secure-storage pattern
/// so the choice survives a cold start without adding a new dependency.
class LocaleController {
  LocaleController({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            ) {
    _restore();
  }

  static const _kLocale = 'valuadis_rent_locale';

  final FlutterSecureStorage _storage;
  final ValueNotifier<Locale?> locale = ValueNotifier<Locale?>(null);

  Future<void> _restore() async {
    final saved = await _storage.read(key: _kLocale);
    if (saved != null && saved.isNotEmpty) {
      locale.value = Locale(saved);
    }
  }

  Future<void> setLocale(Locale? value) async {
    locale.value = value;
    if (value == null) {
      await _storage.delete(key: _kLocale);
    } else {
      await _storage.write(key: _kLocale, value: value.languageCode);
    }
  }

  void dispose() {
    locale.dispose();
  }
}
