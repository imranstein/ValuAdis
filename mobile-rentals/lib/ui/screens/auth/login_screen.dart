import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../blocs/auth/auth_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../widgets/brand.dart';
import '../../widgets/buttons.dart';
import '../../widgets/inputs.dart';
import 'signup_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _submit() {
    FocusScope.of(context).unfocus();
    context.read<AuthBloc>().add(
          AuthLoginRequested(_email.text.trim(), _password.text),
        );
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(),
      body: SafeArea(
        child: BlocConsumer<AuthBloc, AuthState>(
          listener: (context, state) {
            if (state.status == AuthStatus.failure && state.message != null) {
              ScaffoldMessenger.of(context)
                ..hideCurrentSnackBar()
                ..showSnackBar(SnackBar(content: Text(state.message!)));
            }
          },
          builder: (context, state) {
            final loading = state.status == AuthStatus.authenticating;
            return SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const BrandMark(size: 34),
                  const SizedBox(height: 8),
                  Text('Sign in to your registry account',
                      style: AppType.body(c, color: c.inkMuted)),
                  const SizedBox(height: 28),
                  AppTextField(
                    label: 'Email',
                    controller: _email,
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: Icons.mail_outline,
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 16),
                  AppTextField(
                    label: 'Password',
                    controller: _password,
                    obscure: true,
                    prefixIcon: Icons.lock_outline,
                    textInputAction: TextInputAction.done,
                  ),
                  const SizedBox(height: 26),
                  PrimaryButton(
                    label: 'Sign in',
                    loading: loading,
                    onPressed: loading ? null : _submit,
                  ),
                  const SizedBox(height: 16),
                  Center(
                    child: TextButton(
                      onPressed: () => Navigator.of(context).pushReplacement(
                          MaterialPageRoute(
                              builder: (_) => const SignupScreen())),
                      child: Text.rich(
                        TextSpan(
                          style: AppType.label(c, color: c.inkMuted),
                          children: [
                            const TextSpan(text: 'New here?  '),
                            TextSpan(
                                text: 'Create an account',
                                style: AppType.label(c, color: c.green)
                                    .copyWith(fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ),
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
