import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:image_picker/image_picker.dart';

import '../api/api_client.dart';
import '../models/application.dart';
import '../models/contract.dart';
import '../models/listing.dart';
import '../models/owner_listing.dart';
import '../models/property_photo.dart';
import '../models/rent_index.dart';

/// Carries a user-facing message for a failed rentals call (e.g. an out-of-band
/// offer's 422). Screens surface [message] directly.
class RentalsException implements Exception {
  RentalsException(this.message, {this.statusCode});
  final String message;
  final int? statusCode;
  @override
  String toString() => message;
}

class Paged<T> {
  const Paged(this.items, this.total);
  final List<T> items;
  final int total;
}

/// All calls target the stable citizen-facing /api/v1/rentals/* surface plus the
/// shared /api/v1/properties create endpoint.
class RentalsRepository {
  RentalsRepository(this._client);

  final ApiClient _client;

  // --- Renter: browse + apply -------------------------------------------------

  Future<Paged<Listing>> browse({
    String? subCity,
    int? bedrooms,
    double? maxRent,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final res = await _client.get('/rentals/listings', query: {
        if (subCity != null && subCity.isNotEmpty) 'district': subCity,
        'bedrooms': ?bedrooms,
        // band_max filters listings whose lower bound is within the budget.
        'band_max': ?maxRent,
        'skip': skip,
        'limit': limit,
      });
      return _pagedListings(res.data);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load listings.');
    }
  }

  Future<Listing> getListing(String publicId) async {
    try {
      final res = await _client.get('/rentals/listings/$publicId');
      return Listing.fromJson(_data(res.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load this listing.');
    }
  }

  Future<void> apply(String publicId, double offeredRent, String? message) async {
    try {
      await _client.post('/rentals/listings/$publicId/applications', data: {
        'offered_rent': offeredRent,
        if (message != null && message.isNotEmpty) 'message': message,
      });
    } on DioException catch (e) {
      throw _asException(e, 'Could not submit your application.');
    }
  }

  Future<List<RentalApplication>> myApplications() async {
    try {
      final res = await _client.get('/rentals/my-applications');
      return _listOf(res.data, RentalApplication.fromJson);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load your applications.');
    }
  }

  // --- Owner: listings + inbox ------------------------------------------------

  Future<int> createProperty(Map<String, dynamic> payload) async {
    try {
      final res = await _client.post('/properties', data: payload);
      final data = _data(res.data);
      if (data is Map<String, dynamic> && data['id'] != null) {
        return data['id'] as int;
      }
      throw RentalsException('Property was created but no id was returned.');
    } on DioException catch (e) {
      throw _asException(e, 'Could not register the property.');
    }
  }

  Future<OwnerListing> createListing(int propertyId, String? notes) async {
    try {
      final res = await _client.post('/rentals/listings', data: {
        'property_id': propertyId,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      });
      return OwnerListing.fromJson(_data(res.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _asException(e, 'Could not submit the listing.');
    }
  }

  Future<List<OwnerListing>> myListings() async {
    try {
      final res = await _client.get('/rentals/my-listings');
      return _listOf(res.data, OwnerListing.fromJson);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load your listings.');
    }
  }

  Future<void> withdrawListing(String publicId, String reason) async {
    try {
      await _client.post('/rentals/listings/$publicId/withdraw',
          data: {'reason': reason});
    } on DioException catch (e) {
      throw _asException(e, 'Could not withdraw the listing.');
    }
  }

  Future<List<RentalApplication>> listingApplications(String publicId) async {
    try {
      final res = await _client.get('/rentals/listings/$publicId/applications');
      return _listOf(res.data, RentalApplication.fromJson);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load applications for this listing.');
    }
  }

  Future<void> decideApplication(int applicationId, String action,
      {String? reason}) async {
    try {
      await _client.post('/rentals/applications/$applicationId/decision',
          data: {'action': action, 'reason': ?reason});
    } on DioException catch (e) {
      throw _asException(e, 'Could not update the application.');
    }
  }

  // --- Owner: property photos --------------------------------------------------

  Future<List<PropertyPhoto>> propertyPhotos(int propertyId) async {
    try {
      final res = await _client.get('/properties/$propertyId/photos');
      return _listOf(res.data, PropertyPhoto.fromJson);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load photos.');
    }
  }

  /// Bearer headers for a raw `Image`/`CachedNetworkImage` fetch of a photo
  /// that is not on a published listing (those are public; drafts are not).
  Future<Map<String, String>> photoAuthHeaders() => _client.authHeaders();

  Future<PropertyPhoto> uploadPropertyPhoto(
    int propertyId,
    XFile file, {
    void Function(int sent, int total)? onProgress,
  }) async {
    try {
      final bytes = await file.readAsBytes();
      final form = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: file.name),
      });
      final res = await _client.postForm(
        '/properties/$propertyId/photos',
        data: form,
        onSendProgress: onProgress,
      );
      return PropertyPhoto.fromJson(_data(res.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _asException(e, 'Could not upload the photo.');
    }
  }

  Future<void> deletePropertyPhoto(int propertyId, int photoId) async {
    try {
      await _client.delete('/properties/$propertyId/photos/$photoId');
    } on DioException catch (e) {
      throw _asException(e, 'Could not delete the photo.');
    }
  }

  // --- Shared: contracts + index ---------------------------------------------

  Future<List<TenancyContract>> myContracts() async {
    try {
      final res = await _client.get('/rentals/my-contracts');
      return _listOf(res.data, TenancyContract.fromJson);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load your contracts.');
    }
  }

  Future<Uint8List> downloadContractPdf(String contractNo) async {
    try {
      final res = await _client.raw.get<List<int>>(
        '/rentals/contracts/$contractNo/pdf',
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList(res.data ?? const []);
    } on DioException catch (e) {
      throw _asException(e, 'Could not download the contract PDF.');
    }
  }

  Future<Uint8List> downloadListingAgreementPdf(String publicId) async {
    try {
      final res = await _client.raw.get<List<int>>(
        '/rentals/listings/$publicId/agreement',
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList(res.data ?? const []);
    } on DioException catch (e) {
      throw _asException(e, 'Could not download the listing agreement.');
    }
  }

  Future<List<RentIndexRow>> rentIndex() async {
    try {
      final res = await _client.get('/rentals/index');
      return _listOf(res.data, RentIndexRow.fromJson);
    } on DioException catch (e) {
      throw _asException(e, 'Could not load the rent index.');
    }
  }

  // --- helpers ----------------------------------------------------------------

  Paged<Listing> _pagedListings(dynamic payload) {
    if (payload is! Map<String, dynamic>) return const Paged([], 0);
    final list = (payload['data'] as List? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(Listing.fromJson)
        .toList();
    final total = payload['total'] as int? ?? list.length;
    return Paged(list, total);
  }

  List<T> _listOf<T>(dynamic payload, T Function(Map<String, dynamic>) fromJson) {
    final data = _data(payload);
    if (data is! List) return [];
    return data.whereType<Map<String, dynamic>>().map(fromJson).toList();
  }

  dynamic _data(dynamic payload) {
    if (payload is Map<String, dynamic> && payload.containsKey('data')) {
      return payload['data'];
    }
    return payload;
  }

  RentalsException _asException(DioException e, String fallback) {
    final code = e.response?.statusCode;
    final data = e.response?.data;
    String message = fallback;
    if (data is Map) {
      final detail = data['detail'] ?? data['message'];
      if (detail is String) message = detail;
    }
    return RentalsException(message, statusCode: code);
  }
}
