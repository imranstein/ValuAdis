import 'package:equatable/equatable.dart';

abstract class SyncEvent extends Equatable {
  const SyncEvent();

  @override
  List<Object?> get props => [];
}

class SyncTriggered extends SyncEvent {}

class ConnectivityChanged extends SyncEvent {
  final bool isOnline;

  const ConnectivityChanged(this.isOnline);

  @override
  List<Object?> get props => [isOnline];
}

class SyncStatusRequested extends SyncEvent {}
