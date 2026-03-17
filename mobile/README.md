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

## API base URL

Default: `http://localhost:8000`. Override at run time:

```bash
flutter run --dart-define=API_BASE_URL=http://192.168.1.100:8000
```

## Structure

- `lib/core/` – constants, utils
- `lib/data/` – models, repositories, SQLite (database_helper), Hive, API client
- `lib/bloc/` – auth, property, sync
- `lib/services/` – GPS
- `lib/presentation/` – screens (login, property list, property create, map), widgets
