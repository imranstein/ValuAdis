import '../datasources/local/database_helper.dart';
import '../models/photo.dart';

class PhotoRepository {
  final DatabaseHelper _db = DatabaseHelper.instance;

  Future<int> addPhoto(Photo photo) async {
    final db = await _db.database;
    return db.insert('photos', photo.toMap());
  }

  Future<List<Photo>> getPhotosForProperty(int propertyId) async {
    final db = await _db.database;
    final maps = await db.query(
      'photos',
      where: 'property_id = ?',
      whereArgs: [propertyId],
      orderBy: 'created_at DESC',
    );
    return maps.map((m) => Photo.fromMap(m)).toList();
  }
}
