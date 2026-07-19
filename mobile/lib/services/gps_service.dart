import 'package:geolocator/geolocator.dart';

import '../core/constants.dart';

class GPSService {
  Future<Position> getCurrentPosition() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled');
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }

    return await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
  }

  Stream<Position> getPositionStream() {
    return Geolocator.getPositionStream(
      locationSettings: LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    );
  }

  bool isWithinEthiopianBounds(double lat, double lon) {
    return lat >= AppConstants.ethiopiaLatMin &&
        lat <= AppConstants.ethiopiaLatMax &&
        lon >= AppConstants.ethiopiaLonMin &&
        lon <= AppConstants.ethiopiaLonMax;
  }
}
