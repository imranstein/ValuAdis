import '../bloc/auth/auth_bloc.dart';
import '../bloc/property/property_bloc.dart';
import '../bloc/quick_valuation/quick_valuation_bloc.dart';
import '../bloc/sync/sync_bloc.dart';
import '../bloc/valuation/valuation_bloc.dart';
import '../bloc/vehicle/vehicle_bloc.dart';
import '../data/datasources/remote/api_client.dart';
import '../data/repositories/auth_repository.dart';
import '../data/repositories/property_repository.dart';
import '../../core/constants.dart';
import '../data/repositories/photo_repository.dart';
import '../data/repositories/quick_valuation_repository.dart';
import '../data/repositories/valuation_repository.dart';
import '../data/repositories/vehicle_repository.dart';

final blocProviders = _BlocProviders();

class _BlocProviders {
  final AuthRepository _authRepo = AuthRepository();
  final PropertyRepository _propertyRepo = PropertyRepository();
  PhotoRepository _photoRepo = PhotoRepository();
  final ValuationRepository _valuationRepo = ValuationRepository();
  late final VehicleRepository _vehicleRepo;
  late final QuickValuationRepository _quickValuationRepo;
  late final AuthBloc _authBloc;
  late final PropertyBloc _propertyBloc;
  late final SyncBloc _syncBloc;
  late final ValuationBloc _valuationBloc;
  late final VehicleBloc _vehicleBloc;
  late final QuickValuationBloc _quickValuationBloc;
  final ApiClient _apiClient = ApiClient(
    enableSslPinning: AppConstants.enableSslPinning,
    pinnedSha256: AppConstants.sslPinnedSha256,
    maxRetries: 2,
    requestTimeout: const Duration(seconds: 30),
  );

  _BlocProviders() {
    _authBloc = AuthBloc(_authRepo);
    _propertyBloc = PropertyBloc(_propertyRepo);
    _valuationBloc = ValuationBloc(_valuationRepo);
    _vehicleRepo = VehicleRepository(_apiClient);
    _quickValuationRepo = QuickValuationRepository(_apiClient);
    _vehicleBloc = VehicleBloc(_vehicleRepo);
    _quickValuationBloc = QuickValuationBloc(_quickValuationRepo);
    _syncBloc = SyncBloc(
      _propertyRepo,
      _valuationRepo,
      _apiClient,
      null,
      AppConstants.enablePeriodicSync,
      AppConstants.periodicSyncInterval,
    );
  }

  AuthBloc get authBloc => _authBloc;
  PropertyBloc get propertyBloc => _propertyBloc;
  SyncBloc get syncBloc => _syncBloc;
  ValuationBloc get valuationBloc => _valuationBloc;
  VehicleBloc get vehicleBloc => _vehicleBloc;
  QuickValuationBloc get quickValuationBloc => _quickValuationBloc;
  PhotoRepository get photoRepository => _photoRepo;
  set photoRepository(PhotoRepository value) => _photoRepo = value;
  ValuationRepository get valuationRepository => _valuationRepo;
  ApiClient get apiClient => _apiClient;
}
