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

/// Phase G Amharic localization proof. Mirrors journey_test.dart's SHOT:name /
/// host-screencap pattern: prints a marker, dwells so the host watcher can
/// `adb exec-out screencap`, and (for the last shot) the host toggles system
/// dark mode on the marker before capturing. Run:
///   flutter drive --driver=test_driver/integration_test.dart \
///     --target=integration_test/amharic_proof_test.dart -d emulator-5554 \
///     --dart-define=API_BASE_URL=http://10.0.2.2:8123
void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
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

  Future<void> shot(WidgetTester t, String name, {int dwellMs = 6000}) async {
    debugPrint('SHOT:$name');
    await settle(t, ms: dwellMs);
  }

  Future<void> login(WidgetTester t, String email, String password,
      String signInLabel) async {
    final fields = find.byType(TextField);
    await t.enterText(fields.at(0), email);
    await t.enterText(fields.at(1), password);
    await t.pump(const Duration(milliseconds: 200));
    await t.tap(find.text(signInLabel));
  }

  testWidgets('Amharic localization proof', (tester) async {
    await TokenStorage().clear();
    await tester.pumpWidget(buildApp(TokenStorage()));
    await settle(tester, ms: 3500);

    // --- Renter login (English default locale) ---
    await waitFor(tester, find.text('I already have an account'));
    await tester.tap(find.text('I already have an account'));
    await settle(tester);
    await login(tester, 'mobile.renter@example.com', 'ProofPass1!', 'Sign in');
    await waitFor(tester, find.byType(ListingCard), timeoutMs: 20000);
    await settle(tester, ms: 1200);

    // --- Switch to Profile, toggle Amharic ---
    await tester.tap(find.text('Profile').last);
    await settle(tester, ms: 1200);
    // "አማርኛ" is the language-chip label — identical text in both the en and
    // am ARB files, so it is findable before the locale switch too.
    await waitFor(tester, find.text('አማርኛ'));
    await tester.tap(find.text('አማርኛ'));
    await settle(tester, ms: 1200);
    await shot(tester, 'mobile-am-profile-language');

    // --- Browse (now rendering Amharic) ---
    await tester.tap(find.text('ያስሱ'));
    await waitFor(tester, find.byType(ListingCard), timeoutMs: 20000);
    await settle(tester, ms: 1000);
    await shot(tester, 'mobile-am-browse');

    // --- Listing detail ---
    await tester.tap(find.byType(ListingCard).first);
    await settle(tester, ms: 2200);
    await waitFor(tester, find.text('የተፈቀደ የኪራይ ክልል'));
    await shot(tester, 'mobile-am-listing-detail');

    // --- Apply sheet ---
    if (find.text('ያመልክቱ').evaluate().isNotEmpty) {
      await tester.tap(find.text('ያመልክቱ').first);
      await waitFor(tester, find.text('ለኪራይ ያመልክቱ'));
      await shot(tester, 'mobile-am-apply-sheet');
      await tester.tapAt(const Offset(200, 70)); // dismiss sheet via barrier
      await settle(tester);
    }
    if (find.byIcon(Icons.arrow_back).evaluate().isNotEmpty) {
      await tester.tap(find.byIcon(Icons.arrow_back).first);
      await settle(tester);
    }

    // --- Sign out (Amharic profile), sign in as owner ---
    await tester.tap(find.text('መገለጫ').last);
    await settle(tester, ms: 1000);
    if (find.text('ውጣ').evaluate().isNotEmpty) {
      await tester.tap(find.text('ውጣ'));
      await settle(tester, ms: 2000);
    }
    await waitFor(tester, find.text('መለያ አለኝ'));
    await tester.tap(find.text('መለያ አለኝ'));
    await settle(tester);
    await login(tester, 'mobile.owner@example.com', 'ProofPass1!', 'ይግቡ');
    await waitFor(tester, find.text('የኔ ማስታወቂያዎች'), timeoutMs: 20000);
    await settle(tester, ms: 1500);
    await shot(tester, 'mobile-am-owner-listings');

    // --- Dark mode: host toggles system night mode on this marker, then
    // waits a beat before screencapping the same owner-listings screen. ---
    await shot(tester, 'mobile-am-dark-mode', dwellMs: 7000);

    debugPrint('SHOT:done');
  });
}
