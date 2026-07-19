import 'constants.dart';

class AppUtils {
  AppUtils._();

  static bool isWithinEthiopianBounds(double lat, double lon) {
    return lat >= AppConstants.ethiopiaLatMin &&
        lat <= AppConstants.ethiopiaLatMax &&
        lon >= AppConstants.ethiopiaLonMin &&
        lon <= AppConstants.ethiopiaLonMax;
  }

  static String formatArea(double sqm) {
    if (sqm >= 10000) {
      return '${(sqm / 10000).toStringAsFixed(2)} ha';
    }
    return '${sqm.toStringAsFixed(2)} sqm';
  }

  static String syncStatusLabel(String status) {
    switch (status) {
      case 'pending':
        return 'Pending sync';
      case 'syncing':
        return 'Syncing...';
      case 'synced':
        return 'Synced';
      case 'failed':
        return 'Sync failed';
      default:
        return status;
    }
  }
}
