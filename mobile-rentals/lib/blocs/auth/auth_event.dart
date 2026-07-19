part of 'auth_bloc.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();
  @override
  List<Object?> get props => [];
}

class AuthCheckRequested extends AuthEvent {
  const AuthCheckRequested();
}

class AuthLoginRequested extends AuthEvent {
  const AuthLoginRequested(this.email, this.password);
  final String email;
  final String password;
  @override
  List<Object?> get props => [email, password];
}

class AuthSignupRequested extends AuthEvent {
  const AuthSignupRequested({
    required this.fullName,
    required this.email,
    required this.phone,
    required this.password,
    required this.municipality,
    required this.faydaId,
    required this.accountType,
  });

  final String fullName;
  final String email;
  final String phone;
  final String password;
  final String municipality;
  final String faydaId;
  final AccountType accountType;

  @override
  List<Object?> get props =>
      [fullName, email, phone, password, municipality, faydaId, accountType];
}

class AuthProfileRefreshed extends AuthEvent {
  const AuthProfileRefreshed();
}

class AuthLogoutRequested extends AuthEvent {
  const AuthLogoutRequested();
}

class AuthSessionExpired extends AuthEvent {
  const AuthSessionExpired();
}
