import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/models/session_user.dart';
import '../../data/repositories/auth_repository.dart';

part 'auth_event.dart';
part 'auth_state.dart';

/// Owns the session lifecycle: startup check, login, citizen signup, profile
/// refresh (for owner-verification changes), logout, and forced expiry.
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc(this._repository) : super(const AuthState()) {
    on<AuthCheckRequested>(_onCheck);
    on<AuthLoginRequested>(_onLogin);
    on<AuthSignupRequested>(_onSignup);
    on<AuthProfileRefreshed>(_onProfileRefreshed);
    on<AuthLogoutRequested>(_onLogout);
    on<AuthSessionExpired>(_onSessionExpired);
  }

  final AuthRepository _repository;

  Future<void> _onCheck(
      AuthCheckRequested event, Emitter<AuthState> emit) async {
    if (!await _repository.hasSession()) {
      emit(const AuthState(status: AuthStatus.unauthenticated));
      return;
    }
    final user = await _repository.fetchMe();
    if (user == null) {
      emit(const AuthState(status: AuthStatus.unauthenticated));
    } else {
      emit(AuthState(status: AuthStatus.authenticated, user: user));
    }
  }

  Future<void> _onLogin(
      AuthLoginRequested event, Emitter<AuthState> emit) async {
    emit(const AuthState(status: AuthStatus.authenticating));
    final result = await _repository.login(event.email, event.password);
    _emitResult(result, emit);
  }

  Future<void> _onSignup(
      AuthSignupRequested event, Emitter<AuthState> emit) async {
    emit(const AuthState(status: AuthStatus.authenticating));
    final result = await _repository.signup(
      fullName: event.fullName,
      email: event.email,
      phone: event.phone,
      password: event.password,
      municipality: event.municipality,
      faydaId: event.faydaId,
      accountType: event.accountType,
    );
    _emitResult(result, emit);
  }

  Future<void> _onProfileRefreshed(
      AuthProfileRefreshed event, Emitter<AuthState> emit) async {
    final user = await _repository.fetchMe();
    if (user != null && state.isAuthenticated) {
      emit(AuthState(status: AuthStatus.authenticated, user: user));
    }
  }

  Future<void> _onLogout(
      AuthLogoutRequested event, Emitter<AuthState> emit) async {
    await _repository.logout();
    emit(const AuthState(status: AuthStatus.unauthenticated));
  }

  Future<void> _onSessionExpired(
      AuthSessionExpired event, Emitter<AuthState> emit) async {
    await _repository.logout();
    emit(const AuthState(
      status: AuthStatus.unauthenticated,
      message: 'Your session expired. Please sign in again.',
    ));
  }

  void _emitResult(AuthResult result, Emitter<AuthState> emit) {
    if (result.ok) {
      emit(AuthState(status: AuthStatus.authenticated, user: result.user));
    } else {
      emit(AuthState(status: AuthStatus.failure, message: result.message));
    }
  }
}
