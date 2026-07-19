import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../widgets/brand.dart';

/// Plain-language explainer of the legal basis and how the registry protects
/// both sides. No fabricated statistics.
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(title: const Text('About & the law')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(24, 8, 24, 32),
          children: [
            const BrandMark(size: 32),
            const SizedBox(height: 8),
            Text('A government-mediated rental registry for Addis Ababa.',
                style: AppType.body(c, color: c.inkSecondary)
                    .copyWith(fontSize: 16, height: 1.5)),
            const SizedBox(height: 24),
            _Section(
              title: 'The law: Proclamation 1320/2024',
              body:
                  'Ethiopia\'s Rent Control and Administration Proclamation requires '
                  'residential rental contracts to be written and registered with the '
                  'district housing administration. Rent increases are capped, and '
                  'Addis Ababa set the ceiling at 11.5% for 2026/27. This app is the '
                  'digital way to meet that mandate.',
            ),
            _Section(
              title: 'Certified prices, not broker guesses',
              body:
                  'Every listing carries a rent band from an official valuation. You '
                  'apply at any amount inside the band; owners choose a tenant, not a '
                  'price war. There is no bidding.',
            ),
            _Section(
              title: 'Registered contracts',
              body:
                  'When an owner accepts you, a rental officer registers the tenancy '
                  'and issues a contract with a public contract number. The contract '
                  'becomes active once your deposit receipt is recorded at the '
                  'administration.',
            ),
            _Section(
              title: 'Your data',
              body:
                  'Your Fayda ID and phone are used to verify you and appear only on '
                  'your own contracts, never on public listings. Officers verify owner '
                  'accounts before a listing can be published.',
            ),
            _Section(
              title: 'What is not here yet',
              body:
                  'Deposits are recorded, not held in custody, in this version. There '
                  'is no in-app chat; contact details are on the registered contract. '
                  'Photo upload and Amharic are on the way.',
            ),
            const SizedBox(height: 8),
            Center(
              child: Text('Operated with the Addis Ababa Housing Administration',
                  textAlign: TextAlign.center,
                  style: AppType.caption(c, color: c.inkMuted)),
            ),
          ],
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.body});
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppType.headline(c)),
          const SizedBox(height: 6),
          Text(body,
              style: AppType.body(c, color: c.inkSecondary)
                  .copyWith(height: 1.55)),
        ],
      ),
    );
  }
}
