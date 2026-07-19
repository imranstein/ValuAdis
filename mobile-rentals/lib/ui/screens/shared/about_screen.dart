import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/brand.dart';

/// Plain-language explainer of the legal basis and how the registry protects
/// both sides. No fabricated statistics.
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(title: Text(l10n.screenTitleAbout)),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(24, 8, 24, 32),
          children: [
            const BrandMark(size: 32),
            const SizedBox(height: 8),
            Text(l10n.aboutIntro,
                style: AppType.body(c, color: c.inkSecondary)
                    .copyWith(fontSize: 16, height: 1.5)),
            const SizedBox(height: 24),
            _Section(title: l10n.aboutLawTitle, body: l10n.aboutLawBody),
            _Section(
                title: l10n.aboutCertifiedTitle, body: l10n.aboutCertifiedBody),
            _Section(
                title: l10n.welcomePoint2Title, body: l10n.aboutContractsBody),
            _Section(title: l10n.aboutDataTitle, body: l10n.aboutDataBody),
            _Section(
                title: l10n.aboutMissingTitle, body: l10n.aboutMissingBody),
            const SizedBox(height: 8),
            Center(
              child: Text(l10n.aboutFooter,
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
