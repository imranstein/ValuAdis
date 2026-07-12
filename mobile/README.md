# ValuAdis Mobile

Offline-first Flutter app for Ethiopian property valuers. BLoC state management, SQLite + Hive local storage, GPS boundary capture with flutter_map.

## Prerequisites

- Flutter 3.x (e.g. 3.16+)
- Dart 3.2+

## First-time setup

If the project was created manually (no `android/` or `ios/` yet), generate platform code:

```bash
cd mobile
flutter create .   # adds android/, ios/, etc. without overwriting lib/ or pubspec.yaml
```

## Run

From the `mobile` directory (with Flutter on your PATH):

```bash
cd mobile
flutter create .   # only needed once if android/ and ios/ are missing
flutter pub get
flutter run
```

Or use the script:

```bash
cd mobile && ./scripts/setup_and_run.sh
```

Use **Continue offline (demo)** on the login screen to try the app without a backend. Add properties and draw boundaries on the map.

## Environment configuration

All environment configuration is passed with `--dart-define` at build/run time; there is no build-flavor machinery.

### API base URL (`API_BASE_URL`)

Default: `http://localhost:8000` (for local development against the FastAPI dev server). The app appends `/api/v1` itself, so pass the origin only — never include `/api` or `/api/v1` in the value.

```bash
# Physical device on the same network as your dev machine
flutter run --dart-define=API_BASE_URL=http://192.168.1.100:8000

# Android emulator: localhost inside the emulator is the emulator itself.
# Use 10.0.2.2, which the emulator maps to the host machine.
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000

# iOS simulator: localhost works as-is (shares the host network), no override needed.

# Staging / production build
flutter build apk --release --dart-define=API_BASE_URL=https://staging-api.valuadis.example.com
```

The same `--dart-define` flags work for `flutter run`, `flutter build`, and `flutter test`.

### Offline demo login (`VALUADIS_ALLOW_OFFLINE_DEMO`)

The **Continue offline (demo)** button on the login screen stores placeholder demo tokens and is a development convenience only. It is enabled by default in debug/profile builds and disabled in release builds. To force it on in a release build (e.g. an internal demo APK):

```bash
flutter build apk --release --dart-define=VALUADIS_ALLOW_OFFLINE_DEMO=true
```

Do not enable it for production releases: the demo tokens are not real credentials and would be sent to the configured API.

### Other flags

- `VALUADIS_ENABLE_PERIODIC_SYNC` (default `false`) and `VALUADIS_PERIODIC_SYNC_SECONDS` (default `900`)
- `VALUADIS_ENABLE_SSL_PINNING` (default `false`) and `VALUADIS_SSL_PINNED_SHA256`

## Structure

- `lib/core/` – constants, utils
- `lib/data/` – models, repositories, SQLite (database_helper), Hive, API client
- `lib/bloc/` – auth, property, sync
- `lib/services/` – GPS
- `lib/presentation/` – screens (login, property list, property create, map), widgets
