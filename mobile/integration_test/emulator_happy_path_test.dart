import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:valuadis/presentation/app.dart';
import 'package:valuadis/presentation/widgets/property_card.dart';
import 'helpers/test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('13.1 emulator happy path: offline login to detail + valuation', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ValuAdisApp());
    await pumpFrames(tester, count: 6);

    expect(find.text('Welcome to ValuAdis'), findsOneWidget);
    await tester.tap(find.text('Continue offline'));
    await pumpFrames(tester, count: 8);

    if (find.text('Add property').evaluate().isNotEmpty) {
      await tester.tap(find.text('Add property'));
    } else {
      await tester.tap(find.text('New'));
    }
    await pumpFrames(tester, count: 6);

    final addressField = find.byType(TextFormField).at(0);
    await tester.enterText(addressField, 'Bole Demo Property');

    final propertyTypeField = find.byType(TextFormField).at(1);
    await tester.enterText(propertyTypeField, 'residential');

    await tester.tap(find.text('Save property'));
    await pumpFrames(tester, count: 6);

    await tester.tap(find.text('Properties'));
    await pumpFrames(tester, count: 6);

    await tester.tap(find.byType(PropertyCard).first);
    await pumpFrames(tester, count: 6);

    await tester.tap(find.byIcon(Icons.edit_outlined));
    await pumpFrames(tester, count: 6);

    await tester.enterText(
      find.byKey(const Key('edit-address-field')),
      'Bole Updated Property',
    );
    await tester.tap(find.text('Save'));
    await pumpFrames(tester, count: 6);

    expect(find.text('Bole Updated Property'), findsOneWidget);
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
    await pumpFrames(tester, count: 6);

    for (var i = 0; i < 12; i += 1) {
      await tester.pump(const Duration(milliseconds: 500));
      if (find.text('Latest valuation').evaluate().isNotEmpty &&
          find.textContaining('Market: 100000.00').evaluate().isNotEmpty &&
          find.textContaining('Taxable: 85000.00').evaluate().isNotEmpty) {
        break;
      }
    }

    expect(find.text('Latest valuation'), findsOneWidget);
    expect(find.textContaining('Market: 100000.00'), findsOneWidget);
    expect(find.textContaining('Taxable: 85000.00'), findsOneWidget);
    expect(find.text('No photos yet'), findsOneWidget);
  });

  testWidgets('13.2 offline path blocks property save until address is entered',
      (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ValuAdisApp());
    await pumpFrames(tester, count: 6);

    expect(find.text('Welcome to ValuAdis'), findsOneWidget);
    await tester.tap(find.text('Continue offline'));
    await pumpFrames(tester, count: 8);

    await tester.tap(find.text('New'));
    await pumpFrames(tester, count: 6);

    await tester.tap(find.text('Save property'));
    await pumpFrames(tester, count: 4);
    expect(find.text('Enter address'), findsOneWidget);

    await tester.enterText(
        find.byType(TextFormField).at(0), 'Validation Property');
    await tester.tap(find.text('Save property'));
    await pumpFrames(tester, count: 6);

    await tester.tap(find.byIcon(Icons.home).last);
    await pumpUntil(
      tester,
      () => find.text('Validation Property').evaluate().isNotEmpty,
      maxTicks: 60,
    );

    expect(find.text('Validation Property'), findsOneWidget);
  });
}
