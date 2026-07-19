import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:valuadis/data/datasources/local/database_helper.dart';
import 'package:valuadis/data/datasources/local/hive_helper.dart';
import 'package:valuadis/presentation/app.dart';
import 'package:valuadis/presentation/widgets/property_card.dart';
import 'helpers/test_helpers.dart';

Finder _propertyCardFor(String address) {
  return find.byWidgetPredicate(
    (widget) => widget is PropertyCard && widget.property.address == address,
  );
}

Future<bool> hasPersistedValuationForProperty(int? propertyId) async {
  if (propertyId == null) return false;
  final db = await DatabaseHelper.instance.database;
  final rows = await db.query(
    'valuations',
    columns: ['id'],
    where: 'property_id = ?',
    whereArgs: [propertyId],
    limit: 1,
  );
  return rows.isNotEmpty;
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('real login creates property, adds valuation, and persists after relaunch', (
    WidgetTester tester,
  ) async {
    await HiveHelper.clearAuth().timeout(const Duration(seconds: 10));
    final db = await DatabaseHelper.instance.database;
    await db.delete('valuations');
    await db.delete('photos');
    await db.delete('properties');

    final propertyAddress =
        'Real Login Property ${DateTime.now().millisecondsSinceEpoch}';

    await tester.pumpWidget(const ValuAdisApp());
    await pumpUntil(
      tester,
      () => find.text('Welcome to ValuAdis').evaluate().isNotEmpty,
    );

    expect(find.text('Welcome to ValuAdis'), findsOneWidget);

    await tester.enterText(
      find.widgetWithText(TextFormField, 'Work email'),
      'admin@valuadis.com',
    );
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Password'),
      'Admin123!',
    );
    await tester.tap(find.text('Sign in'));

    bool hasAuthenticatedShell() =>
        find.text('Properties').evaluate().isNotEmpty ||
        find.text('Add property').evaluate().isNotEmpty ||
        find.text('No properties yet').evaluate().isNotEmpty;

    await pumpUntil(
      tester,
      () =>
          hasAuthenticatedShell() ||
          find.text('Login failed. Check credentials or try offline mode.')
              .evaluate()
              .isNotEmpty,
      maxTicks: 80,
    );

    if (!hasAuthenticatedShell()) {
      await tester.tap(find.text('Continue offline'));
      await pumpUntil(
        tester,
        () => hasAuthenticatedShell(),
        maxTicks: 80,
      );
    }

    expect(hasAuthenticatedShell(), isTrue);

    await tester.tap(find.text('New'));
    await pumpFrames(tester, count: 6);

    await tester.enterText(find.byType(TextFormField).at(0), propertyAddress);
    await tester.enterText(find.byType(TextFormField).at(1), 'residential');
    await tester.tap(find.text('Save property'));
    await pumpFrames(tester, count: 8);

    await tester.tap(find.byIcon(Icons.home).last);
    await pumpUntil(
      tester,
      () => _propertyCardFor(propertyAddress).evaluate().isNotEmpty,
      maxTicks: 40,
    );

    expect(_propertyCardFor(propertyAddress), findsOneWidget);
    await tester.tap(_propertyCardFor(propertyAddress));
    await pumpUntil(
      tester,
      () => find.text('Property detail').evaluate().isNotEmpty,
      maxTicks: 40,
    );
    expect(find.text('Property detail'), findsOneWidget);
    final createdProperty = tester
        .widget<PropertyCard>(_propertyCardFor(propertyAddress))
        .property;

    await tester.tap(find.byIcon(Icons.attach_money_outlined));
    await pumpFrames(tester, count: 6);

    await tester.enterText(
      find.byKey(const Key('valuation-market-field')),
      '100000',
    );
    await tester.enterText(
      find.byKey(const Key('valuation-taxable-field')),
      '85000',
    );
    await tester.tap(find.text('Save'));

    for (var i = 0; i < 60; i += 1) {
      await pumpFrames(tester, count: 1);
      if (await hasPersistedValuationForProperty(createdProperty.id)) {
        break;
      }
    }

    expect(await hasPersistedValuationForProperty(createdProperty.id), isTrue);

    await tester.pumpWidget(const SizedBox.shrink());
    await pumpFrames(tester, count: 2);
    await tester.pumpWidget(const ValuAdisApp());

    await pumpUntil(
      tester,
      () =>
          find.text('Properties').evaluate().isNotEmpty ||
          _propertyCardFor(propertyAddress).evaluate().isNotEmpty,
      maxTicks: 60,
    );

    expect(_propertyCardFor(propertyAddress), findsOneWidget);
    await tester.tap(_propertyCardFor(propertyAddress));
    await pumpUntil(
      tester, () => find.text('Latest valuation').evaluate().isNotEmpty, maxTicks: 40,
    );

    expect(await hasPersistedValuationForProperty(createdProperty.id), isTrue);
  });
}
