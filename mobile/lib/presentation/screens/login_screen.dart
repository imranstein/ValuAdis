import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/auth/auth_bloc.dart';
import '../../bloc/auth/auth_event.dart';
import '../../bloc/auth/auth_state.dart';
import '../../core/constants.dart';
import '../theme/app_theme.dart';
import '../widgets/shared_ui.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  String? _formError;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.page),
            child: AppCard(
              child: Form(
                key: _formKey,
                child: BlocConsumer<AuthBloc, AuthState>(
                  listener: (context, state) {
                    if (state.status == AuthStatus.failure && state.message != null) {
                      setState(() {
                        _formError = state.message;
                      });
                    }

                    if (state.status != AuthStatus.failure &&
                        _formError != null) {
                      setState(() {
                        _formError = null;
                      });
                    }
                  },
                  builder: (context, state) {
                    final loading = state.status == AuthStatus.loading;

                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const SizedBox(height: AppSpacing.sm),
                        AppSectionHeader(
                          title: 'Welcome to ${AppConstants.appName}',
                          subtitle:
                              'Sign in to continue valuation work from field or office.',
                        ),
                        const SizedBox(height: AppSpacing.md),
                        TextFormField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          autofillHints: const [AutofillHints.username],
                          decoration: const InputDecoration(
                            labelText: 'Work email',
                            prefixIcon: Icon(Icons.email_outlined),
                            hintText: 'you@organization.gov.et',
                          ),
                          validator: (v) =>
                              (v == null || v.trim().isEmpty) ? 'Enter email' : null,
                        ),
                        const SizedBox(height: AppSpacing.md),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: true,
                          autofillHints: const [AutofillHints.password],
                          decoration: const InputDecoration(
                            labelText: 'Password',
                            prefixIcon: Icon(Icons.lock_outlined),
                            hintText: '••••••••',
                          ),
                          validator: (v) => (v == null || v.isEmpty)
                              ? 'Enter password'
                              : null,
                        ),
                        const SizedBox(height: AppSpacing.md),
                        if (_formError != null) ...[
                          Container(
                            padding: const EdgeInsets.all(AppSpacing.sm),
                            decoration: BoxDecoration(
                              color: colorScheme.error.withOpacity(0.08),
                              borderRadius: AppRadius.smRadius,
                            ),
                            child: Text(
                              _formError!,
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: colorScheme.error,
                                    fontWeight: FontWeight.w600,
                                  ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                          const SizedBox(height: AppSpacing.md),
                        ],
                        FilledButton(
                          onPressed: loading
                              ? null
                              : () {
                                  if (_formKey.currentState?.validate() ?? false) {
                                    setState(() => _formError = null);
                                    context.read<AuthBloc>().add(
                                      AuthLoginRequested(
                                        email: _emailController.text.trim(),
                                        password: _passwordController.text,
                                      ),
                                    );
                                  }
                                },
                          child: loading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Text('Sign in'),
                        ),
                        if (AppConstants.allowOfflineDemo) ...[
                          const SizedBox(height: AppSpacing.md),
                          OutlinedButton(
                            onPressed: loading
                                ? null
                                : () {
                                    context.read<AuthBloc>().add(
                                      AuthOfflineRequested(),
                                    );
                                  },
                            child: const Text('Continue offline'),
                          ),
                          const SizedBox(height: AppSpacing.md),
                          Text(
                            'Offline keeps local data usable, and sync resumes when network returns.',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: colorScheme.onSurfaceVariant,
                                ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
