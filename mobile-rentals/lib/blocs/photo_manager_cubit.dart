import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';

import '../core/constants.dart';
import '../data/models/property_photo.dart';
import '../data/repositories/rentals_repository.dart';

enum PhotoLoadStatus { initial, loading, ready, error }

/// State for the owner's photo manager: the loaded gallery plus in-flight
/// upload progress, kept separate from [AsyncCubit] because an upload
/// mutates the list rather than replacing it wholesale.
class PhotoManagerState extends Equatable {
  const PhotoManagerState({
    this.status = PhotoLoadStatus.initial,
    this.photos = const [],
    this.error,
    this.uploading = false,
    this.uploadProgress = 0,
  });

  final PhotoLoadStatus status;
  final List<PropertyPhoto> photos;
  final String? error;
  final bool uploading;
  final double uploadProgress;

  bool get isReady => status == PhotoLoadStatus.ready;
  bool get isError => status == PhotoLoadStatus.error;
  bool get canAddMore => photos.length < AppConstants.maxPhotosPerProperty;

  PhotoManagerState copyWith({
    PhotoLoadStatus? status,
    List<PropertyPhoto>? photos,
    String? error,
    bool? uploading,
    double? uploadProgress,
  }) {
    return PhotoManagerState(
      status: status ?? this.status,
      photos: photos ?? this.photos,
      error: error,
      uploading: uploading ?? this.uploading,
      uploadProgress: uploadProgress ?? this.uploadProgress,
    );
  }

  @override
  List<Object?> get props =>
      [status, photos, error, uploading, uploadProgress];
}

/// Loads, uploads to, and deletes from one property's photo gallery. Client
/// side enforces the same 8-photo / 5MB limits the backend does, so the
/// renter sees an honest error before a doomed upload starts.
class PhotoManagerCubit extends Cubit<PhotoManagerState> {
  PhotoManagerCubit(this._repo, this.propertyId)
      : super(const PhotoManagerState());

  final RentalsRepository _repo;
  final int propertyId;

  Future<void> load() async {
    emit(state.copyWith(status: PhotoLoadStatus.loading));
    try {
      final photos = await _repo.propertyPhotos(propertyId);
      emit(state.copyWith(status: PhotoLoadStatus.ready, photos: photos));
    } on RentalsException catch (e) {
      emit(state.copyWith(status: PhotoLoadStatus.error, error: e.message));
    }
  }

  /// Returns a user-facing error message, or null on success.
  Future<String?> upload(XFile file) async {
    if (!state.canAddMore) {
      return 'A property may have at most '
          '${AppConstants.maxPhotosPerProperty} photos.';
    }
    final size = await file.length();
    if (size > AppConstants.maxPhotoSizeBytes) {
      final maxMb = AppConstants.maxPhotoSizeBytes ~/ (1024 * 1024);
      return 'Photo exceeds the maximum size of ${maxMb}MB.';
    }

    emit(state.copyWith(uploading: true, uploadProgress: 0));
    try {
      final photo = await _repo.uploadPropertyPhoto(
        propertyId,
        file,
        onProgress: (sent, total) {
          if (total > 0) {
            emit(state.copyWith(uploadProgress: sent / total));
          }
        },
      );
      emit(state.copyWith(
        uploading: false,
        photos: [...state.photos, photo],
      ));
      return null;
    } on RentalsException catch (e) {
      emit(state.copyWith(uploading: false));
      return e.message;
    }
  }

  /// Returns a user-facing error message, or null on success. Removes the
  /// photo optimistically and restores it if the delete call fails.
  Future<String?> delete(int photoId) async {
    final previous = state.photos;
    emit(state.copyWith(
        photos: previous.where((p) => p.id != photoId).toList()));
    try {
      await _repo.deletePropertyPhoto(propertyId, photoId);
      return null;
    } on RentalsException catch (e) {
      emit(state.copyWith(photos: previous));
      return e.message;
    }
  }
}
