import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:valuadis_rent/blocs/auth/auth_bloc.dart';
import 'package:valuadis_rent/data/models/session_user.dart';
import 'package:valuadis_rent/data/repositories/auth_repository.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late MockAuthRepository repo;

  const renter = SessionUser(accountType: AccountType.renter, id: 1);

  setUpAll(() => registerFallbackValue(AccountType.renter));
  setUp(() => repo = MockAuthRepository());

  group('AuthCheckRequested', () {
    blocTest<AuthBloc, AuthState>(
      'emits unauthenticated when there is no stored session',
      setUp: () => when(repo.hasSession).thenAnswer((_) async => false),
      build: () => AuthBloc(repo),
      act: (bloc) => bloc.add(const AuthCheckRequested()),
      expect: () => [
        const AuthState(status: AuthStatus.unauthenticated),
      ],
    );

    blocTest<AuthBloc, AuthState>(
      'emits authenticated with the user when a session exists',
      setUp: () {
        when(repo.hasSession).thenAnswer((_) async => true);
        when(repo.fetchMe).thenAnswer((_) async => renter);
      },
      build: () => AuthBloc(repo),
      act: (bloc) => bloc.add(const AuthCheckRequested()),
      expect: () => [
        const AuthState(status: AuthStatus.authenticated, user: renter),
      ],
    );

    blocTest<AuthBloc, AuthState>(
      'emits unauthenticated when the stored token no longer resolves a user',
      setUp: () {
        when(repo.hasSession).thenAnswer((_) async => true);
        when(repo.fetchMe).thenAnswer((_) async => null);
      },
      build: () => AuthBloc(repo),
      act: (bloc) => bloc.add(const AuthCheckRequested()),
      expect: () => [
        const AuthState(status: AuthStatus.unauthenticated),
      ],
    );
  });

  group('AuthLoginRequested', () {
    blocTest<AuthBloc, AuthState>(
      'emits authenticating then authenticated on success',
      setUp: () => when(() => repo.login(any(), any()))
          .thenAnswer((_) async => const AuthResult.success(renter)),
      build: () => AuthBloc(repo),
      act: (bloc) =>
          bloc.add(const AuthLoginRequested('r@example.com', 'Password1')),
      expect: () => [
        const AuthState(status: AuthStatus.authenticating),
        const AuthState(status: AuthStatus.authenticated, user: renter),
      ],
    );

    blocTest<AuthBloc, AuthState>(
      'emits authenticating then failure with the message on bad credentials',
      setUp: () => when(() => repo.login(any(), any())).thenAnswer(
          (_) async => const AuthResult.failure('Login failed.')),
      build: () => AuthBloc(repo),
      act: (bloc) =>
          bloc.add(const AuthLoginRequested('r@example.com', 'wrong')),
      expect: () => [
        const AuthState(status: AuthStatus.authenticating),
        const AuthState(status: AuthStatus.failure, message: 'Login failed.'),
      ],
    );
  });

  group('AuthSignupRequested', () {
    blocTest<AuthBloc, AuthState>(
      'emits authenticating then authenticated on successful signup',
      setUp: () => when(() => repo.signup(
            fullName: any(named: 'fullName'),
            email: any(named: 'email'),
            phone: any(named: 'phone'),
            password: any(named: 'password'),
            municipality: any(named: 'municipality'),
            faydaId: any(named: 'faydaId'),
            accountType: any(named: 'accountType'),
          )).thenAnswer((_) async => const AuthResult.success(renter)),
      build: () => AuthBloc(repo),
      act: (bloc) => bloc.add(const AuthSignupRequested(
        fullName: 'Ada Lovelace',
        email: 'ada@example.com',
        phone: '0912345678',
        password: 'Password1',
        municipality: 'Bole',
        faydaId: '123456',
        accountType: AccountType.renter,
      )),
      expect: () => [
        const AuthState(status: AuthStatus.authenticating),
        const AuthState(status: AuthStatus.authenticated, user: renter),
      ],
    );
  });

  group('AuthLogoutRequested / AuthSessionExpired', () {
    blocTest<AuthBloc, AuthState>(
      'logout clears the session and emits unauthenticated',
      setUp: () => when(repo.logout).thenAnswer((_) async {}),
      build: () => AuthBloc(repo),
      act: (bloc) => bloc.add(const AuthLogoutRequested()),
      expect: () => [
        const AuthState(status: AuthStatus.unauthenticated),
      ],
      verify: (_) => verify(repo.logout).called(1),
    );

    blocTest<AuthBloc, AuthState>(
      'a forced expiry logs out and surfaces a re-login message',
      setUp: () => when(repo.logout).thenAnswer((_) async {}),
      build: () => AuthBloc(repo),
      act: (bloc) => bloc.add(const AuthSessionExpired()),
      expect: () => [
        isA<AuthState>()
            .having((s) => s.status, 'status', AuthStatus.unauthenticated)
            .having((s) => s.message, 'message', isNotNull),
      ],
    );
  });
}
