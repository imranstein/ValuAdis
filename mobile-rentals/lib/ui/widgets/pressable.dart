import 'package:flutter/material.dart';

import '../../core/theme/motion.dart';

/// Wraps any tappable child with a subtle scale-down on press (0.97, 120ms
/// ease-out), the app's universal "the interface heard you" feedback. Respects
/// reduced-motion by skipping the scale.
class Pressable extends StatefulWidget {
  const Pressable({
    super.key,
    required this.child,
    this.onTap,
    this.scale = 0.97,
    this.borderRadius,
  });

  final Widget child;
  final VoidCallback? onTap;
  final double scale;
  final BorderRadius? borderRadius;

  @override
  State<Pressable> createState() => _PressableState();
}

class _PressableState extends State<Pressable> {
  bool _down = false;

  void _set(bool value) {
    if (widget.onTap == null) return;
    setState(() => _down = value);
  }

  @override
  Widget build(BuildContext context) {
    final reduceMotion = MediaQuery.maybeOf(context)?.disableAnimations ?? false;
    final target = (_down && !reduceMotion) ? widget.scale : 1.0;
    return GestureDetector(
      onTapDown: (_) => _set(true),
      onTapUp: (_) => _set(false),
      onTapCancel: () => _set(false),
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedScale(
        scale: target,
        duration: Motion.press,
        curve: Motion.easeOutQuart,
        child: widget.child,
      ),
    );
  }
}
