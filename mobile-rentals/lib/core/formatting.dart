import 'package:intl/intl.dart';

/// Money and date formatting for the registry. ETB is rendered in mono type at
/// the call site; this file only produces the strings.
class Fmt {
  Fmt._();

  static final NumberFormat _etb = NumberFormat('#,##0', 'en_US');
  static final DateFormat _date = DateFormat('d MMM yyyy');
  static final DateFormat _monthDay = DateFormat('d MMM');

  /// "27,500 ETB" style rent label. The localized "/month" suffix is appended
  /// at the call site (AppLocalizations.perMonthSuffixShort) so the per-month
  /// abbreviation renders in the active locale, not a hardcoded "/mo".
  static String rent(num value) => '${_etb.format(value)} ETB';

  static String date(DateTime? value) =>
      value == null ? '—' : _date.format(value.toLocal());

  static String shortDate(DateTime? value) =>
      value == null ? '—' : _monthDay.format(value.toLocal());

  /// Turns a snake_case backend enum into a human label ("needs_repair" ->
  /// "Needs repair").
  static String humanize(String? raw) {
    if (raw == null || raw.isEmpty) return '';
    final words = raw.replaceAll('_', ' ').trim();
    return words[0].toUpperCase() + words.substring(1);
  }
}
