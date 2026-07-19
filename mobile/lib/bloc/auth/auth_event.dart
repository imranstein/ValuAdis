import 'package:equatable/equatable.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AuthCheckRequested extends AuthEvent {}

class AuthLoginRequested extends AuthEvent {
  final String email;
  final String password;

  const AuthLoginRequested({required this.email, required this.password});

  @override
  List<Object?> get props => [email, password];
}

class AuthLogoutRequested extends AuthEvent {}

class AuthSessionExpired extends AuthEvent {
  final String message;

  const AuthSessionExpired({required this.message});

  @override
  List<Object?> get props => [message];
}

class AuthOfflineRequested extends AuthEvent {}
