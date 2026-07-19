import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/motion.dart';
import 'states.dart';

/// A real, cached property photo. [url] is the opaque relative path the
/// backend returns (`/api/v1/properties/{id}/photos/{id}/file`); this widget
/// resolves it against the API origin, shows a skeleton shimmer while it
/// loads, and falls back to [errorPlaceholder] on a failed fetch (offline,
/// deleted photo, or a draft listing viewed without [headers]).
class NetworkPhoto extends StatelessWidget {
  const NetworkPhoto({
    super.key,
    required this.url,
    required this.errorPlaceholder,
    this.headers,
    this.fit = BoxFit.cover,
  });

  final String url;
  final Widget errorPlaceholder;
  final Map<String, String>? headers;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final absoluteUrl = url.startsWith('http')
        ? url
        : '${AppConstants.apiBaseUrl}$url';
    return CachedNetworkImage(
      imageUrl: absoluteUrl,
      httpHeaders: (headers != null && headers!.isNotEmpty) ? headers : null,
      fit: fit,
      fadeInDuration: Motion.hero,
      fadeInCurve: Motion.easeOutQuint,
      placeholder: (_, _) => Shimmer(child: ColoredBox(color: c.surfaceSunken)),
      errorWidget: (_, _, _) => errorPlaceholder,
    );
  }
}
