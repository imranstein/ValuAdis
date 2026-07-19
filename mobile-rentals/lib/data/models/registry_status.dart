import 'package:flutter/widgets.dart';

import '../../l10n/app_localizations.dart';

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

  /// English fallback label. Pure Dart (no [BuildContext]) so it stays
  /// testable in isolation; [localizedLabelOf] is what the UI actually
  /// renders and falls back to this when localization isn't available
  /// (e.g. a widget test built without [AppLocalizations] delegates).
  static String labelOf(String? raw) {
    if (raw == null || raw.isEmpty) return 'Unknown';
    return _labels[raw.toLowerCase()] ??
        (raw[0].toUpperCase() + raw.substring(1).replaceAll('_', ' '));
  }

  /// Localized display label for a raw backend status. Covers listing status
  /// (published/pending_review/rented/withdrawn/draft), application status
  /// (pending/accepted/rejected/withdrawn), and contract status
  /// (active/terminated/expired) using the glossary terms.
  static String localizedLabelOf(BuildContext context, String? raw) {
    final l10n = AppLocalizations.of(context);
    if (l10n == null || raw == null || raw.isEmpty) return labelOf(raw);
    switch (raw.toLowerCase()) {
      case 'pending':
        return l10n.statusPending;
      case 'accepted':
        return l10n.statusAccepted;
      case 'rejected':
        return l10n.statusRejected;
      case 'withdrawn':
        return l10n.statusWithdrawn;
      case 'draft':
        return l10n.statusDraft;
      case 'pending_review':
        return l10n.statusPendingReview;
      case 'published':
        return l10n.statusPublished;
      case 'rented':
        return l10n.statusRented;
      case 'active':
        return l10n.statusActive;
      case 'terminated':
        return l10n.statusTerminated;
      case 'expired':
        return l10n.statusExpired;
      default:
        return labelOf(raw);
    }
  }
}
