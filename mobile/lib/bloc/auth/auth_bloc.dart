import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/repositories/auth_repository.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc(this._authRepository) : super(const AuthState()) {
    on<AuthCheckRequested>(_onCheckRequested);
    on<AuthLoginRequested>(_onLoginRequested);
    on<AuthLogoutRequested>(_onLogoutRequested);
    on<AuthSessionExpired>(_onSessionExpired);
    on<AuthOfflineRequested>(_onOfflineRequested);
  }

  void _onCheckRequested(AuthCheckRequested event, Emitter<AuthState> emit) {
    if (_authRepository.isLoggedIn) {
      emit(const AuthState(status: AuthStatus.authenticated));
    } else {
      emit(const AuthState(status: AuthStatus.unauthenticated));
    }
  }

  Future<void> _onLoginRequested(
    AuthLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthState(status: AuthStatus.loading));
    final success = await _authRepository.login(event.email, event.password);
    if (success) {
      emit(const AuthState(status: AuthStatus.authenticated));
    } else {
      emit(
        const AuthState(
          status: AuthStatus.failure,
          message: 'Login failed. Check credentials or try offline mode.',
        ),
      );
    }
  }

  Future<void> _onLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await _authRepository.logout();
    emit(const AuthState(status: AuthStatus.unauthenticated));
  }

  Future<void> _onOfflineRequested(
    AuthOfflineRequested event,
    Emitter<AuthState> emit,
  ) async {
    try {
      await _authRepository.loginOffline();
      emit(const AuthState(status: AuthStatus.authenticated));
    } on StateError catch (error) {
      emit(AuthState(status: AuthStatus.failure, message: error.message));
    }
  }

  Future<void> _onSessionExpired(
    AuthSessionExpired event,
    Emitter<AuthState> emit,
  ) async {
    await _authRepository.logout();
    emit(
      AuthState(
        status: AuthStatus.failure,
        message: event.message,
      ),
    );
  }
}
