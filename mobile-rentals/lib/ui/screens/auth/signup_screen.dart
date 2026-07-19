import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/auth/auth_bloc.dart';
import '../../../core/constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/session_user.dart';
import '../../../l10n/app_localizations.dart';
import '../../widgets/brand.dart';
import '../../widgets/buttons.dart';
import '../../widgets/inputs.dart';
import '../../widgets/pressable.dart';
import 'login_screen.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  AccountType _type = AccountType.renter;
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _fayda = TextEditingController();
  final _password = TextEditingController();
  String _subCity = AppConstants.addisSubCities.first;

  String? _formError;

  @override
  void dispose() {
    for (final ctrl in [_name, _email, _phone, _fayda, _password]) {
      ctrl.dispose();
    }
    super.dispose();
  }

  String? _validate() {
    final l10n = AppLocalizations.of(context)!;
    if (_name.text.trim().length < 3) return l10n.validationFullName;
    if (!_email.text.contains('@')) return l10n.validationEmail;
    if (_phone.text.trim().length < 9) return l10n.validationPhone;
    if (_fayda.text.trim().length < 6) return l10n.validationFaydaId;
    final pw = _password.text;
    if (pw.length < 8) return l10n.validationPasswordLength;
    if (!pw.contains(RegExp(r'[A-Z]'))) {
      return l10n.validationPasswordUppercase;
    }
    if (!pw.contains(RegExp(r'[0-9]'))) return l10n.validationPasswordNumber;
    return null;
  }

  void _submit() {
    final error = _validate();
    setState(() => _formError = error);
    if (error != null) return;
    FocusScope.of(context).unfocus();
    context.read<AuthBloc>().add(AuthSignupRequested(
          fullName: _name.text.trim(),
          email: _email.text.trim(),
          phone: _phone.text.trim(),
          password: _password.text,
          municipality: _subCity,
          faydaId: _fayda.text.trim(),
          accountType: _type,
        ));
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(),
      body: SafeArea(
        child: BlocConsumer<AuthBloc, AuthState>(
          listener: (context, state) {
            if (state.status == AuthStatus.failure && state.message != null) {
              setState(() => _formError = state.message);
            }
          },
          builder: (context, state) {
            final loading = state.status == AuthStatus.authenticating;
            return SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const BrandMark(size: 32),
                  const SizedBox(height: 8),
                  Text(l10n.signupSubtitle,
                      style: AppType.body(c, color: c.inkMuted)),
                  const SizedBox(height: 22),
                  Row(
                    children: [
                      Expanded(
                        child: _TypeCard(
                          icon: Icons.search,
                          title: l10n.signupTypeRenterTitle,
                          selected: _type == AccountType.renter,
                          onTap: () =>
                              setState(() => _type = AccountType.renter),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _TypeCard(
                          icon: Icons.home_work_outlined,
                          title: l10n.signupTypeOwnerTitle,
                          selected: _type == AccountType.propertyOwner,
                          onTap: () => setState(
                              () => _type = AccountType.propertyOwner),
                        ),
                      ),
                    ],
                  ),
                  if (_type == AccountType.propertyOwner)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: _OwnerNote(),
                    ),
                  const SizedBox(height: 20),
                  AppTextField(
                      label: l10n.fieldFullName,
                      controller: _name,
                      prefixIcon: Icons.person_outline,
                      textInputAction: TextInputAction.next),
                  const SizedBox(height: 14),
                  AppTextField(
                      label: l10n.fieldEmail,
                      controller: _email,
                      keyboardType: TextInputType.emailAddress,
                      prefixIcon: Icons.mail_outline,
                      textInputAction: TextInputAction.next),
                  const SizedBox(height: 14),
                  AppTextField(
                    label: l10n.fieldPhone,
                    controller: _phone,
                    keyboardType: TextInputType.phone,
                    prefixIcon: Icons.phone_outlined,
                    hint: l10n.hintPhoneFormat,
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(RegExp(r'[0-9+]'))
                    ],
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 14),
                  AppDropdownField<String>(
                    label: l10n.fieldSubCity,
                    value: _subCity,
                    items: AppConstants.addisSubCities,
                    onChanged: (v) => setState(() => _subCity = v ?? _subCity),
                  ),
                  const SizedBox(height: 14),
                  AppTextField(
                    label: l10n.fieldFaydaId,
                    controller: _fayda,
                    prefixIcon: Icons.badge_outlined,
                    hint: l10n.hintFaydaId,
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 14),
                  AppTextField(
                    label: l10n.fieldPassword,
                    controller: _password,
                    obscure: true,
                    prefixIcon: Icons.lock_outline,
                    hint: l10n.hintPasswordRules,
                    textInputAction: TextInputAction.done,
                  ),
                  if (_formError != null) ...[
                    const SizedBox(height: 16),
                    _ErrorBanner(message: _formError!),
                  ],
                  const SizedBox(height: 22),
                  PrimaryButton(
                    label: l10n.actionCreateAccountShort,
                    loading: loading,
                    onPressed: loading ? null : _submit,
                  ),
                  const SizedBox(height: 12),
                  Center(
                    child: TextButton(
                      onPressed: () => Navigator.of(context).pushReplacement(
                          MaterialPageRoute(
                              builder: (_) => const LoginScreen())),
                      child: Text(l10n.authAlreadyHaveAccount,
                          style: AppType.label(c, color: c.green)),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _TypeCard extends StatelessWidget {
  const _TypeCard({
    required this.icon,
    required this.title,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Pressable(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 14),
        decoration: BoxDecoration(
          color: selected ? c.greenSoft.withValues(alpha: 0.6) : c.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
              color: selected ? c.green : c.border,
              width: selected ? 1.8 : 1),
        ),
        child: Column(
          children: [
            Icon(icon, color: selected ? c.green : c.inkMuted, size: 24),
            const SizedBox(height: 10),
            Text(title,
                textAlign: TextAlign.center,
                style: AppType.label(c,
                    color: selected ? c.ink : c.inkSecondary,
                    weight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _OwnerNote extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: c.goldWash,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline, size: 17, color: c.gold),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              AppLocalizations.of(context)!.signupOwnerNote,
              style: AppType.caption(c, color: c.inkSecondary)
                  .copyWith(height: 1.4),
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});
  final String message;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: c.dangerWash,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, size: 18, color: c.danger),
          const SizedBox(width: 10),
          Expanded(
              child: Text(message,
                  style: AppType.label(c, color: c.danger))),
        ],
      ),
    );
  }
}
