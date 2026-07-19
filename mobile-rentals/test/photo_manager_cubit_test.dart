import 'dart:typed_data';

import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mocktail/mocktail.dart';
import 'package:valuadis_rent/blocs/photo_manager_cubit.dart';
import 'package:valuadis_rent/core/constants.dart';
import 'package:valuadis_rent/data/models/property_photo.dart';
import 'package:valuadis_rent/data/repositories/rentals_repository.dart';

class MockRentalsRepository extends Mock implements RentalsRepository {}

void main() {
  late MockRentalsRepository repo;

  const propertyId = 42;
  const photoA = PropertyPhoto(id: 1, url: '/api/v1/properties/42/photos/1/file', position: 0);
  const photoB = PropertyPhoto(id: 2, url: '/api/v1/properties/42/photos/2/file', position: 1);

  XFile smallFile() =>
      XFile.fromData(Uint8List(10), name: 'small.jpg');
  XFile oversizedFile() =>
      XFile.fromData(Uint8List(AppConstants.maxPhotoSizeBytes + 1), name: 'big.jpg');

  setUpAll(() {
    registerFallbackValue(smallFile());
  });

  setUp(() => repo = MockRentalsRepository());

  group('load', () {
    blocTest<PhotoManagerCubit, PhotoManagerState>(
      'emits ready with the loaded photos on success',
      setUp: () => when(() => repo.propertyPhotos(propertyId))
          .thenAnswer((_) async => [photoA, photoB]),
      build: () => PhotoManagerCubit(repo, propertyId),
      act: (cubit) => cubit.load(),
      expect: () => [
        const PhotoManagerState(status: PhotoLoadStatus.loading),
        const PhotoManagerState(
            status: PhotoLoadStatus.ready, photos: [photoA, photoB]),
      ],
    );

    blocTest<PhotoManagerCubit, PhotoManagerState>(
      'emits error with the repository message on failure',
      setUp: () => when(() => repo.propertyPhotos(propertyId))
          .thenThrow(RentalsException('Could not load photos.')),
      build: () => PhotoManagerCubit(repo, propertyId),
      act: (cubit) => cubit.load(),
      expect: () => [
        const PhotoManagerState(status: PhotoLoadStatus.loading),
        const PhotoManagerState(
            status: PhotoLoadStatus.error, error: 'Could not load photos.'),
      ],
    );
  });

  group('upload', () {
    test('rejects a photo without calling the repository once at the limit',
        () async {
      final maxed = List.generate(
        AppConstants.maxPhotosPerProperty,
        (i) => PropertyPhoto(id: i, url: '/f/$i', position: i),
      );
      when(() => repo.propertyPhotos(propertyId))
          .thenAnswer((_) async => maxed);
      final cubit = PhotoManagerCubit(repo, propertyId);
      await cubit.load();

      final error = await cubit.upload(smallFile());

      expect(error, contains('at most'));
      verifyNever(() => repo.uploadPropertyPhoto(any(), any()));
    });

    test('rejects an oversized photo without calling the repository',
        () async {
      final cubit = PhotoManagerCubit(repo, propertyId);

      final error = await cubit.upload(oversizedFile());

      expect(error, contains('5MB'));
      verifyNever(() => repo.uploadPropertyPhoto(any(), any()));
    });

    blocTest<PhotoManagerCubit, PhotoManagerState>(
      'appends the uploaded photo on success',
      setUp: () => when(() => repo.uploadPropertyPhoto(propertyId, any(),
              onProgress: any(named: 'onProgress')))
          .thenAnswer((_) async => photoA),
      build: () => PhotoManagerCubit(repo, propertyId),
      act: (cubit) => cubit.upload(smallFile()),
      expect: () => [
        const PhotoManagerState(uploading: true),
        const PhotoManagerState(uploading: false, photos: [photoA]),
      ],
    );

    blocTest<PhotoManagerCubit, PhotoManagerState>(
      'clears the uploading flag and returns the message on failure',
      setUp: () => when(() => repo.uploadPropertyPhoto(propertyId, any(),
              onProgress: any(named: 'onProgress')))
          .thenThrow(RentalsException('Could not upload the photo.')),
      build: () => PhotoManagerCubit(repo, propertyId),
      act: (cubit) => cubit.upload(smallFile()),
      expect: () => [
        const PhotoManagerState(uploading: true),
        const PhotoManagerState(uploading: false),
      ],
    );
  });

  group('delete', () {
    blocTest<PhotoManagerCubit, PhotoManagerState>(
      'removes the photo optimistically and stays removed on success',
      setUp: () => when(() => repo.deletePropertyPhoto(propertyId, photoA.id))
          .thenAnswer((_) async {}),
      build: () => PhotoManagerCubit(repo, propertyId),
      seed: () => const PhotoManagerState(
          status: PhotoLoadStatus.ready, photos: [photoA, photoB]),
      act: (cubit) => cubit.delete(photoA.id),
      expect: () => [
        const PhotoManagerState(status: PhotoLoadStatus.ready, photos: [photoB]),
      ],
    );

    blocTest<PhotoManagerCubit, PhotoManagerState>(
      'restores the photo when the delete call fails',
      setUp: () => when(() => repo.deletePropertyPhoto(propertyId, photoA.id))
          .thenThrow(RentalsException('Could not delete the photo.')),
      build: () => PhotoManagerCubit(repo, propertyId),
      seed: () => const PhotoManagerState(
          status: PhotoLoadStatus.ready, photos: [photoA, photoB]),
      act: (cubit) => cubit.delete(photoA.id),
      expect: () => [
        const PhotoManagerState(status: PhotoLoadStatus.ready, photos: [photoB]),
        const PhotoManagerState(
            status: PhotoLoadStatus.ready, photos: [photoA, photoB]),
      ],
    );
  });
}
