import 'package:flutter/material.dart';

import 'welcome_screen.dart';

/// A nested navigator for the signed-out experience (welcome, login, signup).
/// Keeping it self-contained means that when auth succeeds and the app gate
/// swaps in the home shell, this whole stack is discarded cleanly.
class AuthFlow extends StatelessWidget {
  const AuthFlow({super.key});

  @override
  Widget build(BuildContext context) {
    return Navigator(
      onGenerateRoute: (settings) => MaterialPageRoute(
        settings: settings,
        builder: (_) => const WelcomeScreen(),
      ),
    );
  }
}
