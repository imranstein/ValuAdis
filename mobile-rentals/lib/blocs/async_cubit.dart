import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../data/repositories/rentals_repository.dart';

enum LoadStatus { initial, loading, ready, error }

/// A small typed container for one asynchronous collection/resource. Screens
/// switch on [status] to render skeleton, content, error, or empty honestly.
class AsyncState<T> extends Equatable {
  const AsyncState({this.status = LoadStatus.initial, this.data, this.error});

  final LoadStatus status;
  final T? data;
  final String? error;

  bool get isReady => status == LoadStatus.ready;
  bool get isLoading => status == LoadStatus.loading;
  bool get isError => status == LoadStatus.error;

  AsyncState<T> loading() => AsyncState<T>(status: LoadStatus.loading, data: data);
  AsyncState<T> ready(T value) =>
      AsyncState<T>(status: LoadStatus.ready, data: value);
  AsyncState<T> failed(String message) =>
      AsyncState<T>(status: LoadStatus.error, data: data, error: message);

  @override
  List<Object?> get props => [status, data, error];
}

/// Base cubit that loads a single resource, mapping [RentalsException] messages
/// straight to the error state so the UI can show the real reason.
abstract class AsyncCubit<T> extends Cubit<AsyncState<T>> {
  AsyncCubit() : super(AsyncState<T>());

  Future<T> fetch();

  Future<void> load() async {
    emit(state.loading());
    try {
      emit(state.ready(await fetch()));
    } on RentalsException catch (e) {
      emit(state.failed(e.message));
    } catch (_) {
      emit(state.failed('Something went wrong. Pull to try again.'));
    }
  }

  Future<void> refresh() => load();
}
