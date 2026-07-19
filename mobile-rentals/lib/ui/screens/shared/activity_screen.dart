import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/constants.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../widgets/pills.dart';
import '../../widgets/states.dart';

/// Local status-change feed (no push infrastructure in v1). It derives activity
/// items from the user's applications and contracts and refreshes on open plus a
/// gentle poll, so a decision made server-side surfaces without a manual reload.
class ActivityScreen extends StatefulWidget {
  const ActivityScreen({super.key});

  @override
  State<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityItem {
  const _ActivityItem(this.icon, this.title, this.status, this.when);
  final IconData icon;
  final String title;
  final String status;
  final DateTime? when;
}

class _ActivityScreenState extends State<ActivityScreen> {
  late final RentalsRepository _repo = context.read<RentalsRepository>();
  Timer? _timer;
  bool _loading = true;
  String? _error;
  List<_ActivityItem> _items = const [];

  @override
  void initState() {
    super.initState();
    _load();
    _timer = Timer.periodic(AppConstants.notificationPollInterval, (_) => _load());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final apps = await _repo.myApplications();
      final contracts = await _repo.myContracts();
      final items = <_ActivityItem>[
        for (final a in apps)
          _ActivityItem(
            Icons.assignment_outlined,
            'Application · ${a.propertyAddress ?? a.listingPublicId ?? ''}',
            a.status,
            a.decidedAt ?? a.createdAt,
          ),
        for (final k in contracts)
          _ActivityItem(
            Icons.description_outlined,
            'Contract · ${k.contractNo}',
            k.status,
            k.createdAt,
          ),
      ]..sort((a, b) =>
          (b.when ?? DateTime(0)).compareTo(a.when ?? DateTime(0)));
      if (!mounted) return;
      setState(() {
        _items = items;
        _loading = false;
        _error = null;
      });
    } on RentalsException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.message;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(title: const Text('Activity')),
      body: SafeArea(
        child: _buildBody(c),
      ),
    );
  }

  Widget _buildBody(AppColors c) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return ErrorView(message: _error!, onRetry: _load);
    }
    if (_items.isEmpty) {
      return const EmptyState(
        icon: Icons.notifications_none,
        title: 'Nothing new',
        message:
            'Status changes on your applications and contracts show up here. '
            'This updates automatically while the app is open.',
      );
    }
    return RefreshIndicator(
      color: c.green,
      onRefresh: _load,
      child: ListView.separated(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        itemCount: _items.length,
        separatorBuilder: (_, _) => const SizedBox(height: 10),
        itemBuilder: (context, i) {
          final item = _items[i];
          return StaggeredReveal(
            index: i,
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: c.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: c.border),
              ),
              child: Row(
                children: [
                  Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                        color: c.greenSoft.withValues(alpha: 0.6),
                        borderRadius: BorderRadius.circular(11)),
                    child: Icon(item.icon, size: 19, color: c.green),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item.title,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: AppType.label(c,
                                color: c.ink, weight: FontWeight.w600)),
                        const SizedBox(height: 2),
                        Text(Fmt.date(item.when),
                            style: AppType.caption(c, color: c.inkMuted)),
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  StatusPill(item.status, compact: true),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
