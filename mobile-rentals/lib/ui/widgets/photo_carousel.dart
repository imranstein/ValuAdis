import 'package:flutter/material.dart';

import 'network_photo.dart';

/// Full-bleed swipeable gallery for the listing detail hero. Falls back to a
/// single [placeholder] when a listing has no real photos yet.
class PhotoCarousel extends StatefulWidget {
  const PhotoCarousel({
    super.key,
    required this.urls,
    required this.placeholder,
  });

  final List<String> urls;
  final Widget placeholder;

  @override
  State<PhotoCarousel> createState() => _PhotoCarouselState();
}

class _PhotoCarouselState extends State<PhotoCarousel> {
  final _controller = PageController();
  int _page = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.urls.isEmpty) return widget.placeholder;
    return Stack(
      fit: StackFit.expand,
      children: [
        PageView.builder(
          controller: _controller,
          itemCount: widget.urls.length,
          onPageChanged: (i) => setState(() => _page = i),
          itemBuilder: (_, i) => NetworkPhoto(
            url: widget.urls[i],
            errorPlaceholder: widget.placeholder,
          ),
        ),
        if (widget.urls.length > 1)
          Positioned(
            bottom: 14,
            left: 0,
            right: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                for (var i = 0; i < widget.urls.length; i++)
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.symmetric(horizontal: 3),
                    width: i == _page ? 16 : 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: Colors.white
                          .withValues(alpha: i == _page ? 0.95 : 0.5),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}
