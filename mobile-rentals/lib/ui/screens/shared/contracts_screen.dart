import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';

import '../../../blocs/async_cubit.dart';
import '../../../blocs/cubits.dart';
import '../../../core/formatting.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/contract.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../widgets/buttons.dart';
import '../../widgets/pills.dart';
import '../../widgets/screen_header.dart';
import '../../widgets/states.dart';

class ContractsScreen extends StatelessWidget {
  const ContractsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final cubit = context.read<ContractsCubit>();
    return SafeArea(
      bottom: false,
      child: Column(
        children: [
          const ScreenHeader(
              title: 'My contracts',
              subtitle: 'Registered tenancy agreements'),
          Expanded(
            child: BlocBuilder<ContractsCubit,
                AsyncState<List<TenancyContract>>>(
              builder: (context, state) {
                if (state.isError) {
                  return ErrorView(
                      message: state.error ?? 'Could not load contracts.',
                      onRetry: cubit.load);
                }
                if (!state.isReady) {
                  return const Center(child: CircularProgressIndicator());
                }
                final contracts = state.data!;
                if (contracts.isEmpty) {
                  return const EmptyState(
                    icon: Icons.description_outlined,
                    title: 'No contracts yet',
                    message:
                        'Once an application is accepted and an officer registers '
                        'the tenancy, your contract will appear here with its PDF.',
                  );
                }
                return RefreshIndicator(
                  color: c.green,
                  onRefresh: cubit.refresh,
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: contracts.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 14),
                    itemBuilder: (context, i) => StaggeredReveal(
                      index: i,
                      child: _ContractCard(contract: contracts[i]),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _ContractCard extends StatefulWidget {
  const _ContractCard({required this.contract});
  final TenancyContract contract;

  @override
  State<_ContractCard> createState() => _ContractCardState();
}

class _ContractCardState extends State<_ContractCard> {
  bool _downloading = false;

  Future<void> _download() async {
    setState(() => _downloading = true);
    final repo = context.read<RentalsRepository>();
    try {
      final bytes = await repo.downloadContractPdf(widget.contract.contractNo);
      final dir = await getTemporaryDirectory();
      final file = File(
          '${dir.path}/ValuAdis_${widget.contract.contractNo}.pdf');
      await file.writeAsBytes(bytes);
      await OpenFilex.open(file.path);
    } on RentalsException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(SnackBar(content: Text(e.message)));
      }
    } finally {
      if (mounted) setState(() => _downloading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    final contract = widget.contract;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: c.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Contract',
                        style: AppType.caption(c, color: c.inkMuted)),
                    const SizedBox(height: 2),
                    Text(contract.contractNo,
                        style: AppType.mono(c, size: 16, weight: FontWeight.w700)),
                  ],
                ),
              ),
              StatusPill(contract.status),
            ],
          ),
          const SizedBox(height: 16),
          _row(c, 'Monthly rent', Fmt.rentPerMonth(contract.monthlyRent),
              mono: true),
          _row(c, 'Term',
              '${Fmt.date(contract.startDate)}  ->  ${Fmt.date(contract.endDate)}'),
          if (contract.depositAmount != null)
            _row(c, 'Deposit', Fmt.rent(contract.depositAmount!), mono: true),
          _row(
              c,
              'Deposit receipt',
              contract.depositRecorded
                  ? 'Recorded'
                  : 'Awaiting record',
              valueColor:
                  contract.depositRecorded ? c.green : c.gold),
          const SizedBox(height: 8),
          if (!contract.isActive)
            Container(
              padding: const EdgeInsets.all(11),
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                  color: c.goldWash, borderRadius: BorderRadius.circular(10)),
              child: Text(
                'This contract activates once the officer records your deposit '
                'receipt at the housing administration.',
                style: AppType.caption(c, color: c.inkSecondary)
                    .copyWith(height: 1.4),
              ),
            ),
          GhostButton(
            label: _downloading ? 'Preparing PDF...' : 'Download contract PDF',
            icon: Icons.picture_as_pdf_outlined,
            onPressed: _downloading ? null : _download,
          ),
        ],
      ),
    );
  }

  Widget _row(AppColors c, String label, String value,
      {bool mono = false, Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: AppType.label(c, color: c.inkMuted)),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: mono
                  ? AppType.mono(c,
                      size: 13,
                      weight: FontWeight.w700,
                      color: valueColor ?? c.ink)
                  : AppType.label(c,
                      color: valueColor ?? c.ink, weight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}
