import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../blocs/cubits.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/session_user.dart';
import '../../data/repositories/rentals_repository.dart';
import '../../l10n/app_localizations.dart';
import '../widgets/pressable.dart';
import 'owner/owner_listings_screen.dart';
import 'renter/browse_screen.dart';
import 'shared/contracts_screen.dart';
import 'shared/my_applications_screen.dart';
import 'shared/profile_screen.dart';
import 'shared/rent_index_screen.dart';

/// The signed-in shell. Bottom-nav tabs are data, scoped to the persona: renters
/// browse and track applications; owners manage listings and contracts. Both
/// share the rent index and profile.
class HomeShell extends StatefulWidget {
  const HomeShell({super.key, required this.user});
  final SessionUser user;

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _NavTab {
  const _NavTab(this.icon, this.activeIcon, this.label, this.builder);
  final IconData icon;
  final IconData activeIcon;
  final String label;
  final WidgetBuilder builder;
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  List<_NavTab> _tabs(BuildContext context) {
    final repo = context.read<RentalsRepository>();
    final l10n = AppLocalizations.of(context)!;
    if (widget.user.isOwner) {
      return [
        _NavTab(Icons.home_work_outlined, Icons.home_work, l10n.navListings,
            (_) => BlocProvider(
                create: (_) => MyListingsCubit(repo)..load(),
                child: const OwnerListingsScreen())),
        _NavTab(Icons.description_outlined, Icons.description,
            l10n.navContracts,
            (_) => BlocProvider(
                create: (_) => ContractsCubit(repo)..load(),
                child: const ContractsScreen())),
        _NavTab(Icons.insights_outlined, Icons.insights, l10n.navIndex,
            (_) => BlocProvider(
                create: (_) => RentIndexCubit(repo)..load(),
                child: const RentIndexScreen())),
        _NavTab(Icons.person_outline, Icons.person, l10n.navProfile,
            (_) => ProfileScreen(user: widget.user)),
      ];
    }
    return [
      _NavTab(Icons.explore_outlined, Icons.explore, l10n.navBrowse,
          (_) => BlocProvider(
              create: (_) => BrowseCubit(repo)..load(),
              child: const BrowseScreen())),
      _NavTab(Icons.assignment_outlined, Icons.assignment,
          l10n.navApplications,
          (_) => BlocProvider(
              create: (_) => MyApplicationsCubit(repo)..load(),
              child: const MyApplicationsScreen())),
      _NavTab(Icons.description_outlined, Icons.description,
          l10n.navContracts,
          (_) => BlocProvider(
              create: (_) => ContractsCubit(repo)..load(),
              child: const ContractsScreen())),
      _NavTab(Icons.insights_outlined, Icons.insights, l10n.navIndex,
          (_) => BlocProvider(
              create: (_) => RentIndexCubit(repo)..load(),
              child: const RentIndexScreen())),
      _NavTab(Icons.person_outline, Icons.person, l10n.navProfile,
          (_) => ProfileScreen(user: widget.user)),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final tabs = _tabs(context);
    return Scaffold(
      backgroundColor: c.canvas,
      body: IndexedStack(
        index: _index,
        children: [for (final tab in tabs) tab.builder(context)],
      ),
      bottomNavigationBar: _BottomNav(
        tabs: tabs,
        index: _index,
        onChanged: (i) => setState(() => _index = i),
      ),
    );
  }
}

class _BottomNav extends StatelessWidget {
  const _BottomNav(
      {required this.tabs, required this.index, required this.onChanged});
  final List<_NavTab> tabs;
  final int index;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Container(
      decoration: BoxDecoration(
        color: c.surface,
        border: Border(top: BorderSide(color: c.border)),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 62,
          child: Row(
            children: [
              for (var i = 0; i < tabs.length; i++)
                Expanded(
                  child: Pressable(
                    onTap: () => onChanged(i),
                    scale: 0.9,
                    child: _NavItem(tab: tabs[i], selected: i == index),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({required this.tab, required this.selected});
  final _NavTab tab;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final color = selected ? c.green : c.inkMuted;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(selected ? tab.activeIcon : tab.icon, size: 23, color: color),
        const SizedBox(height: 3),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 2),
          child: Text(tab.label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: AppType.caption(c, color: color).copyWith(
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w500)),
        ),
      ],
    );
  }
}
