import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:wallpaper_manager_flutter/wallpaper_manager_flutter.dart';

extension WallpaperNetworkExtension on WallpaperManagerFlutter {
  Future<bool> setWallpaperFromNetwork(String url, int location) async {
    final file = await DefaultCacheManager().getSingleFile(url);
    await setwallpaperfromFile(file.path, location);
    return true;
  }
}
