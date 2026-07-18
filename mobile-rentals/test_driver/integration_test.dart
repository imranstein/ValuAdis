import 'package:integration_test/integration_test_driver.dart';

/// Plain driver. Screenshots are captured host-side via `adb exec-out screencap`
/// keyed on `SHOT:name` logcat markers printed by the journey test (the in-test
/// takeScreenshot path hangs on Android surface conversion).
Future<void> main() => integrationDriver();
