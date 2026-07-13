import 'package:flutter/material.dart';

import 'data/datasources/local/database_helper.dart';
import 'data/datasources/local/hive_helper.dart';
import 'presentation/app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await HiveHelper.init();
  await DatabaseHelper.instance.database;
  runApp(const ValuAdisApp());
}
