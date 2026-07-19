import 'package:flutter_test/flutter_test.dart';

Future<void> pumpFrames(
  WidgetTester tester, {
  int count = 8,
  Duration step = const Duration(milliseconds: 250),
}) async {
  for (var i = 0; i < count; i += 1) {
    await tester.pump(step);
  }
}

Future<void> pumpUntil(
  WidgetTester tester,
  bool Function() condition, {
  int maxTicks = 40,
  Duration step = const Duration(milliseconds: 250),
}) async {
  for (var i = 0; i < maxTicks; i += 1) {
    if (condition()) {
      return;
    }
    await tester.pump(step);
  }
}

