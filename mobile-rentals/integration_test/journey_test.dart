import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:valuadis_rent/app.dart';
import 'package:valuadis_rent/blocs/auth/auth_bloc.dart';
import 'package:valuadis_rent/core/locale_controller.dart';
import 'package:valuadis_rent/data/api/api_client.dart';
import 'package:valuadis_rent/data/api/token_storage.dart';
import 'package:valuadis_rent/data/repositories/auth_repository.dart';
import 'package:valuadis_rent/data/repositories/rentals_repository.dart';
import 'package:valuadis_rent/ui/widgets/listing_card.dart';

/// Drives both persona journeys against a live backend. At each key state it
/// prints a `SHOT:name` logcat marker and dwells (~6s of pumped frames) so a
/// host-side watcher can `adb exec-out screencap` the visible screen. Run:
///   flutter drive --driver=test_driver/integration_test.dart \
///     --target=integration_test/journey_test.dart -d emulator-5554 \
///     --dart-define=API_BASE_URL=http://10.0.2.2:8055
void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  // Present every pumped frame on the real display so host-side screencap
  // sees the live UI (the default policy renders nothing on-screen).
  binding.framePolicy = LiveTestWidgetsFlutterBindingFramePolicy.fullyLive;

  Widget buildApp(TokenStorage storage) {
    late final AuthBloc authBloc;
    final api = ApiClient(storage,
        onUnauthorized: () => authBloc.add(const AuthSessionExpired()));
    final authRepo = AuthRepository(api, storage);
    authBloc = AuthBloc(authRepo)..add(const AuthCheckRequested());
    return ValuAdisRentApp(
        authBloc: authBloc,
        rentalsRepository: RentalsRepository(api),
        localeController: LocaleController());
  }

  Future<void> settle(WidgetTester t, {int ms = 2200}) async {
    var elapsed = 0;
    while (elapsed < ms) {
      await t.pump(const Duration(milliseconds: 120));
      elapsed += 120;
    }
  }

  Future<bool> waitFor(WidgetTester t, Finder f, {int timeoutMs = 15000}) async {
    var elapsed = 0;
    while (elapsed < timeoutMs) {
      await t.pump(const Duration(milliseconds: 200));
      elapsed += 200;
      if (f.evaluate().isNotEmpty) return true;
    }
    return f.evaluate().isNotEmpty;
  }

  Future<void> shot(WidgetTester t, String name) async {
    debugPrint('SHOT:$name');
    await settle(t, ms: 6000); // dwell so the host watcher can screencap
  }

  Future<void> login(WidgetTester t, String email, String password) async {
    final fields = find.byType(TextField);
    await t.enterText(fields.at(0), email);
    await t.enterText(fields.at(1), password);
    await t.pump(const Duration(milliseconds: 200));
    await t.tap(find.text('Sign in'));
  }

  testWidgets('renter and owner journeys', (tester) async {
    await TokenStorage().clear();
    await tester.pumpWidget(buildApp(TokenStorage()));
    await settle(tester, ms: 3500);

    // --- Welcome (brand) ---
    await waitFor(tester, find.text('Create an account'));
    await shot(tester, '01_welcome');

    // --- Signup design (persona cards) ---
    await tester.tap(find.text('Create an account'));
    await settle(tester);
    if (find.text('List a property').evaluate().isNotEmpty) {
      await tester.tap(find.text('List a property'));
      await settle(tester, ms: 800);
    }
    await shot(tester, '02_signup_owner_persona');
    await tester.pageBack();
    await settle(tester);

    // --- Renter login ---
    await waitFor(tester, find.text('I already have an account'));
    await tester.tap(find.text('I already have an account'));
    await settle(tester);
    await shot(tester, '03_login');
    await login(tester, 'phasedrenter1@example.com', 'Password1');
    await waitFor(tester, find.byType(ListingCard), timeoutMs: 20000);
    await settle(tester, ms: 1500);
    await shot(tester, '04_renter_browse');

    // --- Listing detail ---
    await tester.tap(find.byType(ListingCard).first);
    await settle(tester, ms: 2500);
    await waitFor(tester, find.text('Allowed rent band'));
    await shot(tester, '05_listing_detail');

    // --- Apply sheet ---
    if (find.text('Apply').evaluate().isNotEmpty) {
      await tester.tap(find.text('Apply').first);
      await waitFor(tester, find.text('Apply to rent'));
      await shot(tester, '06_apply_sheet');
      await tester.tapAt(const Offset(200, 70)); // dismiss sheet via barrier
      await settle(tester);
    }

    // back to browse, then tabs
    if (find.byIcon(Icons.arrow_back).evaluate().isNotEmpty) {
      await tester.tap(find.byIcon(Icons.arrow_back).first);
      await settle(tester);
    }
    if (find.text('Applications').evaluate().isNotEmpty) {
      await tester.tap(find.text('Applications').last);
      await settle(tester, ms: 2400);
      await shot(tester, '07_my_applications');
    }
    if (find.text('Index').evaluate().isNotEmpty) {
      await tester.tap(find.text('Index').last);
      await settle(tester, ms: 2400);
      await shot(tester, '08_rent_index');
    }
    if (find.text('Profile').evaluate().isNotEmpty) {
      await tester.tap(find.text('Profile').last);
      await settle(tester, ms: 1600);
      await shot(tester, '09_renter_profile');
      if (find.text('Sign out').evaluate().isNotEmpty) {
        await tester.tap(find.text('Sign out'));
        await settle(tester, ms: 2400);
      }
    }

    // --- Owner login ---
    await waitFor(tester, find.text('I already have an account'));
    await tester.tap(find.text('I already have an account'));
    await settle(tester);
    await login(tester, 'phasedowner1@example.com', 'Password1');
    await settle(tester, ms: 3200);
    await shot(tester, '10_owner_listings');

    // owner listing -> applications inbox
    final ownerCard = find.textContaining('AA-LST');
    if (ownerCard.evaluate().isNotEmpty) {
      await tester.tap(ownerCard.first);
      await settle(tester, ms: 2600);
      await shot(tester, '11_listing_applications');
      if (find.byIcon(Icons.arrow_back).evaluate().isNotEmpty) {
        await tester.tap(find.byIcon(Icons.arrow_back).first);
        await settle(tester);
      }
    }
    if (find.text('Contracts').evaluate().isNotEmpty) {
      await tester.tap(find.text('Contracts').last);
      await settle(tester, ms: 2400);
      await shot(tester, '12_contracts');
    }
    // register a property form
    if (find.text('Listings').evaluate().isNotEmpty) {
      await tester.tap(find.text('Listings').last);
      await settle(tester);
      if (find.byIcon(Icons.add).evaluate().isNotEmpty) {
        await tester.tap(find.byIcon(Icons.add).first);
        await settle(tester, ms: 2000);
        await shot(tester, '13_property_register');
      }
    }
    debugPrint('SHOT:done');
  });
}
