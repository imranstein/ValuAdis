import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../core/formatting.dart';

/// Filled text field: label above, error below, green focus ring. Consistent
/// across auth and the property form.
class AppTextField extends StatelessWidget {
  const AppTextField({
    super.key,
    required this.label,
    this.controller,
    this.hint,
    this.keyboardType,
    this.obscure = false,
    this.error,
    this.prefixIcon,
    this.inputFormatters,
    this.maxLines = 1,
    this.onChanged,
    this.textInputAction,
  });

  final String label;
  final TextEditingController? controller;
  final String? hint;
  final TextInputType? keyboardType;
  final bool obscure;
  final String? error;
  final IconData? prefixIcon;
  final List<TextInputFormatter>? inputFormatters;
  final int maxLines;
  final ValueChanged<String>? onChanged;
  final TextInputAction? textInputAction;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppType.label(c, color: c.inkSecondary)),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          keyboardType: keyboardType,
          obscureText: obscure,
          inputFormatters: inputFormatters,
          maxLines: obscure ? 1 : maxLines,
          onChanged: onChanged,
          textInputAction: textInputAction,
          style: AppType.body(c, color: c.ink),
          cursorColor: c.green,
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: AppType.body(c, color: c.inkMuted),
            prefixIcon:
                prefixIcon == null ? null : Icon(prefixIcon, size: 19, color: c.inkMuted),
            filled: true,
            fillColor: c.surfaceSunken.withValues(alpha: 0.55),
            isDense: true,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            enabledBorder: _border(c.border),
            focusedBorder: _border(c.green, width: 1.6),
            errorBorder: _border(c.danger),
            focusedErrorBorder: _border(c.danger, width: 1.6),
            errorText: error,
            errorStyle: AppType.caption(c, color: c.danger),
          ),
        ),
      ],
    );
  }

  OutlineInputBorder _border(Color color, {double width = 1}) =>
      OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: color, width: width),
      );
}

/// Filled dropdown select styled to match [AppTextField].
class AppDropdownField<T> extends StatelessWidget {
  const AppDropdownField({
    super.key,
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
    this.itemLabel,
    this.hint,
  });

  final String label;
  final T? value;
  final List<T> items;
  final ValueChanged<T?> onChanged;
  final String Function(T)? itemLabel;
  final String? hint;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppType.label(c, color: c.inkSecondary)),
        const SizedBox(height: 6),
        DropdownButtonFormField<T>(
          initialValue: value,
          isExpanded: true,
          icon: Icon(Icons.keyboard_arrow_down_rounded, color: c.inkMuted),
          dropdownColor: c.surface,
          style: AppType.body(c, color: c.ink),
          hint: hint == null
              ? null
              : Text(hint!, style: AppType.body(c, color: c.inkMuted)),
          decoration: InputDecoration(
            filled: true,
            fillColor: c.surfaceSunken.withValues(alpha: 0.55),
            isDense: true,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: c.border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: c.green, width: 1.6),
            ),
          ),
          items: items
              .map((item) => DropdownMenuItem<T>(
                    value: item,
                    child: Text(
                      itemLabel?.call(item) ?? Fmt.humanize(item.toString()),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ))
              .toList(),
          onChanged: onChanged,
        ),
      ],
    );
  }
}
