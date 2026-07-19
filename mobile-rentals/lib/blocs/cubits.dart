import '../data/models/application.dart';
import '../data/models/contract.dart';
import '../data/models/listing.dart';
import '../data/models/owner_listing.dart';
import '../data/models/rent_index.dart';
import '../data/repositories/rentals_repository.dart';
import 'async_cubit.dart';

/// Renter browse with sub-city / bedrooms / max-rent filters. The filter values
/// live on the cubit so the toolbar and the fetch stay in sync.
class BrowseCubit extends AsyncCubit<List<Listing>> {
  BrowseCubit(this._repo);
  final RentalsRepository _repo;

  String? subCity;
  int? bedrooms;
  double? maxRent;

  bool get hasFilters =>
      subCity != null || bedrooms != null || maxRent != null;

  void applyFilters({
    String? subCity,
    int? bedrooms,
    double? maxRent,
  }) {
    this.subCity = subCity;
    this.bedrooms = bedrooms;
    this.maxRent = maxRent;
    load();
  }

  void clearFilters() {
    subCity = null;
    bedrooms = null;
    maxRent = null;
    load();
  }

  @override
  Future<List<Listing>> fetch() async {
    final page = await _repo.browse(
      subCity: subCity,
      bedrooms: bedrooms,
      maxRent: maxRent,
    );
    return page.items;
  }
}

class ListingDetailCubit extends AsyncCubit<Listing> {
  ListingDetailCubit(this._repo, this.publicId);
  final RentalsRepository _repo;
  final String publicId;

  @override
  Future<Listing> fetch() => _repo.getListing(publicId);
}

class MyApplicationsCubit extends AsyncCubit<List<RentalApplication>> {
  MyApplicationsCubit(this._repo);
  final RentalsRepository _repo;

  @override
  Future<List<RentalApplication>> fetch() => _repo.myApplications();
}

class MyListingsCubit extends AsyncCubit<List<OwnerListing>> {
  MyListingsCubit(this._repo);
  final RentalsRepository _repo;

  @override
  Future<List<OwnerListing>> fetch() => _repo.myListings();
}

class ListingApplicationsCubit extends AsyncCubit<List<RentalApplication>> {
  ListingApplicationsCubit(this._repo, this.publicId);
  final RentalsRepository _repo;
  final String publicId;

  @override
  Future<List<RentalApplication>> fetch() =>
      _repo.listingApplications(publicId);

  Future<String?> decide(int applicationId, String action,
      {String? reason}) async {
    try {
      await _repo.decideApplication(applicationId, action, reason: reason);
      await load();
      return null;
    } on RentalsException catch (e) {
      return e.message;
    }
  }
}

class ContractsCubit extends AsyncCubit<List<TenancyContract>> {
  ContractsCubit(this._repo);
  final RentalsRepository _repo;

  @override
  Future<List<TenancyContract>> fetch() => _repo.myContracts();
}

class RentIndexCubit extends AsyncCubit<List<RentIndexRow>> {
  RentIndexCubit(this._repo);
  final RentalsRepository _repo;

  @override
  Future<List<RentIndexRow>> fetch() => _repo.rentIndex();
}
