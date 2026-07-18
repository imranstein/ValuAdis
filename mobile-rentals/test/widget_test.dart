import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:valuadis_rent/core/theme/app_colors.dart';
import 'package:valuadis_rent/data/models/band.dart';
import 'package:valuadis_rent/ui/widgets/band_range_bar.dart';
import 'package:valuadis_rent/ui/widgets/pills.dart';

Widget _wrap(Widget child) => MaterialApp(
      home: AppColorsScope(
        colors: AppColors.light,
        child: Scaffold(body: Center(child: child)),
      ),
    );

void main() {
  testWidgets('StatusPill renders the humane label for a raw status',
      (tester) async {
    await tester.pumpWidget(_wrap(const StatusPill('accepted')));
    expect(find.text('Accepted'), findsOneWidget);
  });

  testWidgets('BandRangeBar renders the band bounds as mono ETB labels',
      (tester) async {
    const band = RentBand(min: 25200, max: 30800, suggested: 28000);
    await tester.pumpWidget(_wrap(const SizedBox(
      width: 300,
      child: BandRangeBar(band: band),
    )));
    expect(find.text('25,200 ETB'), findsOneWidget);
    expect(find.text('30,800 ETB'), findsOneWidget);
  });
}
