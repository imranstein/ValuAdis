/// Maps raw backend status strings (listings, applications, contracts) to a
/// display label and a semantic [StatusKind] that drives the status pill's tone.
/// Pure and centralised so the same "accepted" always reads the same way and can
/// be unit-tested without Flutter.
enum StatusKind { positive, pending, neutral, negative }

class RegistryStatus {
  RegistryStatus._();

  static const Map<String, StatusKind> _kinds = {
    // Applications
    'pending': StatusKind.pending,
    'accepted': StatusKind.positive,
    'rejected': StatusKind.negative,
    'withdrawn': StatusKind.neutral,
    // Listings
    'draft': StatusKind.neutral,
    'pending_review': StatusKind.pending,
    'published': StatusKind.positive,
    'rented': StatusKind.positive,
    // Contracts
    'active': StatusKind.positive,
    'terminated': StatusKind.negative,
    'expired': StatusKind.neutral,
  };

  static const Map<String, String> _labels = {
    'pending': 'Pending',
    'accepted': 'Accepted',
    'rejected': 'Not selected',
    'withdrawn': 'Withdrawn',
    'draft': 'Draft',
    'pending_review': 'Under review',
    'published': 'Published',
    'rented': 'Rented',
    'active': 'Active',
    'terminated': 'Terminated',
    'expired': 'Expired',
  };

  static StatusKind kindOf(String? raw) =>
      _kinds[raw?.toLowerCase()] ?? StatusKind.neutral;

  static String labelOf(String? raw) {
    if (raw == null || raw.isEmpty) return 'Unknown';
    return _labels[raw.toLowerCase()] ??
        (raw[0].toUpperCase() + raw.substring(1).replaceAll('_', ' '));
  }
}
