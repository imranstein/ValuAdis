import 'package:equatable/equatable.dart';

enum AuthStatus { initial, authenticated, unauthenticated, loading, failure }

class AuthState extends Equatable {
  final AuthStatus status;
  final String? message;

  const AuthState({this.status = AuthStatus.initial, this.message});

  @override
  List<Object?> get props => [status, message];
}
