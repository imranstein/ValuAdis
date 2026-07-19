import 'package:equatable/equatable.dart';

class SyncItemStatus extends Equatable {
  final String scope;
  final int id;
  final String status;
  final String? message;

  const SyncItemStatus({
    required this.scope,
    required this.id,
    required this.status,
    this.message,
  });

  @override
  List<Object?> get props => [scope, id, status, message];
}

enum SyncStatus { idle, syncing, synced, failed }

class SyncState extends Equatable {
  final SyncStatus status;
  final String? message;
  final bool isOnline;
  final List<SyncItemStatus> itemStatuses;
  final int pendingItems;

  const SyncState({
    this.status = SyncStatus.idle,
    this.message,
    this.isOnline = true,
    this.itemStatuses = const [],
    this.pendingItems = 0,
  });

  static const _messageSentinel = Object();

  SyncState copyWith({
    SyncStatus? status,
    Object? message = _messageSentinel,
    bool? isOnline,
    List<SyncItemStatus>? itemStatuses,
    int? pendingItems,
  }) {
    return SyncState(
      status: status ?? this.status,
      message: message == _messageSentinel ? this.message : message as String?,
      isOnline: isOnline ?? this.isOnline,
      itemStatuses: itemStatuses ?? this.itemStatuses,
      pendingItems: pendingItems ?? this.pendingItems,
    );
  }

  @override
  List<Object?> get props => [status, message, isOnline, itemStatuses, pendingItems];
}
