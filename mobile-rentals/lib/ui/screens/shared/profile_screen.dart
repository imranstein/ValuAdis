import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/auth/auth_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/session_user.dart';
import '../../widgets/buttons.dart';
import '../../widgets/pressable.dart';
import '../../widgets/screen_header.dart';
import 'about_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key, required this.user});
  final SessionUser user;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    // Prefer the freshest user from the bloc (owner verification can change).
    final current = context.watch<AuthBloc>().state.user ?? user;
    final roleLabel = switch (current.accountType) {
      AccountType.propertyOwner => 'Property owner',
      AccountType.renter => 'Renter',
      AccountType.officer => 'Rental officer',
      AccountType.unknown => 'Citizen',
    };

    return SafeArea(
      bottom: false,
      child: ListView(
        padding: const EdgeInsets.only(bottom: 24),
        children: [
          const ScreenHeader(title: 'Profile'),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundColor: c.greenSoft,
                      child: Text(
                        (current.fullName ?? 'V').characters.first.toUpperCase(),
                        style: AppType.serifDisplay(c, size: 26, color: c.green),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(current.fullName ?? 'Your account',
                              style: AppType.title(c)),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Text(roleLabel,
                                  style: AppType.label(c, color: c.inkMuted)),
                              if (current.isOwner) ...[
                                const SizedBox(width: 8),
                                _VerifyChip(verified: current.ownerVerified),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _InfoCard(rows: [
                  ('Email', current.email),
                  ('Phone', current.phone),
                  ('Fayda ID', current.faydaId),
                  ('Sub-city', current.municipality),
                ]),
                const SizedBox(height: 16),
                _LinkTile(
                  icon: Icons.gavel_outlined,
                  label: 'About & the law',
                  sublabel: 'Proclamation 1320/2024 explained',
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                      builder: (_) => const AboutScreen())),
                ),
                const SizedBox(height: 24),
                GhostButton(
                  label: 'Sign out',
                  icon: Icons.logout,
                  danger: true,
                  onPressed: () =>
                      context.read<AuthBloc>().add(const AuthLogoutRequested()),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _VerifyChip extends StatelessWidget {
  const _VerifyChip({required this.verified});
  final bool verified;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final (fg, bg, label, icon) = verified
        ? (c.green, c.greenSoft, 'Verified', Icons.verified_outlined)
        : (c.gold, c.goldWash, 'Pending', Icons.hourglass_top_outlined);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
          color: bg, borderRadius: BorderRadius.circular(999)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: fg),
          const SizedBox(width: 4),
          Text(label,
              style: AppType.caption(c, color: fg)
                  .copyWith(fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.rows});
  final List<(String, String?)> rows;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final visible = rows.where((r) => r.$2 != null && r.$2!.isNotEmpty).toList();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: c.border),
      ),
      child: Column(
        children: [
          for (var i = 0; i < visible.length; i++) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 13),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(visible[i].$1,
                      style: AppType.label(c, color: c.inkMuted)),
                  Flexible(
                    child: Text(visible[i].$2!,
                        textAlign: TextAlign.right,
                        style: AppType.label(c,
                            color: c.ink, weight: FontWeight.w600)),
                  ),
                ],
              ),
            ),
            if (i < visible.length - 1) Divider(height: 1, color: c.border),
          ],
        ],
      ),
    );
  }
}

class _LinkTile extends StatelessWidget {
  const _LinkTile(
      {required this.icon,
      required this.label,
      required this.sublabel,
      required this.onTap});
  final IconData icon;
  final String label;
  final String sublabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Pressable(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: c.border),
        ),
        child: Row(
          children: [
            Icon(icon, size: 20, color: c.green),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label,
                      style: AppType.label(c,
                          color: c.ink, weight: FontWeight.w600)),
                  Text(sublabel,
                      style: AppType.caption(c, color: c.inkMuted)),
                ],
              ),
            ),
            Icon(Icons.chevron_right, size: 18, color: c.inkMuted),
          ],
        ),
      ),
    );
  }
}
