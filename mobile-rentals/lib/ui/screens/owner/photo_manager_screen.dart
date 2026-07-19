import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';

import '../../../blocs/photo_manager_cubit.dart';
import '../../../core/constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/repositories/rentals_repository.dart';
import '../../widgets/network_photo.dart';
import '../../widgets/pressable.dart';
import '../../widgets/states.dart';

/// Owner photo management for one property: pick from gallery or camera,
/// upload with visible progress, delete. Enforces the 8-photo / 5MB limits
/// client-side (mirroring the backend) so failures are explained, not silent.
class PhotoManagerScreen extends StatelessWidget {
  const PhotoManagerScreen({
    super.key,
    required this.propertyId,
    required this.propertyAddress,
  });

  final int propertyId;
  final String propertyAddress;

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => PhotoManagerCubit(
          context.read<RentalsRepository>(), propertyId)
        ..load(),
      child: _PhotoManagerView(propertyAddress: propertyAddress),
    );
  }
}

class _PhotoManagerView extends StatefulWidget {
  const _PhotoManagerView({required this.propertyAddress});
  final String propertyAddress;

  @override
  State<_PhotoManagerView> createState() => _PhotoManagerViewState();
}

class _PhotoManagerViewState extends State<_PhotoManagerView> {
  late final Future<Map<String, String>> _headersFuture =
      context.read<RentalsRepository>().photoAuthHeaders();

  Future<void> _pick(BuildContext context, ImageSource source) async {
    final cubit = context.read<PhotoManagerCubit>();
    XFile? file;
    try {
      file = await ImagePicker().pickImage(source: source, imageQuality: 85);
    } catch (_) {
      // No camera/gallery on this device or permission denied; ignore silently.
    }
    if (file == null || !context.mounted) return;
    final error = await cubit.upload(file);
    if (!context.mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(content: Text(error)));
    }
  }

  Future<void> _showSourcePicker(BuildContext context) async {
    final c = AppColors.of(context);
    final source = await showModalBottomSheet<ImageSource>(
      context: context,
      backgroundColor: c.surface,
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.photo_library_outlined, color: c.green),
              title: Text('Choose from gallery', style: AppType.body(c)),
              onTap: () => Navigator.of(context).pop(ImageSource.gallery),
            ),
            ListTile(
              leading: Icon(Icons.photo_camera_outlined, color: c.green),
              title: Text('Take a photo', style: AppType.body(c)),
              onTap: () => Navigator.of(context).pop(ImageSource.camera),
            ),
          ],
        ),
      ),
    );
    if (source != null && context.mounted) {
      await _pick(context, source);
    }
  }

  Future<void> _delete(BuildContext context, int photoId) async {
    final c = AppColors.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: c.surface,
        title: Text('Remove this photo?', style: AppType.headline(c)),
        content: Text('This cannot be undone.',
            style: AppType.body(c, color: c.inkSecondary)),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text('Cancel', style: AppType.label(c, color: c.inkMuted))),
          TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: Text('Remove',
                  style: AppType.label(c, color: c.danger)
                      .copyWith(fontWeight: FontWeight.w700))),
        ],
      ),
    );
    if (confirmed != true || !context.mounted) return;
    final error = await context.read<PhotoManagerCubit>().delete(photoId);
    if (!context.mounted || error == null) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(error)));
  }

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Scaffold(
      backgroundColor: c.canvas,
      appBar: AppBar(
        title: const Text('Photos'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(20),
          child: Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Text(widget.propertyAddress,
                style: AppType.caption(c, color: c.inkMuted)),
          ),
        ),
      ),
      body: SafeArea(
        top: false,
        child: BlocBuilder<PhotoManagerCubit, PhotoManagerState>(
          builder: (context, state) {
            if (state.status == PhotoLoadStatus.loading &&
                state.photos.isEmpty) {
              return const Center(child: CircularProgressIndicator());
            }
            if (state.isError && state.photos.isEmpty) {
              return ErrorView(
                message: state.error ?? 'Could not load photos.',
                onRetry: context.read<PhotoManagerCubit>().load,
              );
            }
            return Column(
              children: [
                if (state.uploading)
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: state.uploadProgress > 0
                            ? state.uploadProgress
                            : null,
                        minHeight: 4,
                        backgroundColor: c.surfaceSunken,
                        valueColor: AlwaysStoppedAnimation(c.green),
                      ),
                    ),
                  ),
                Expanded(
                  child: _PhotoGrid(
                    state: state,
                    headersFuture: _headersFuture,
                    onAdd: state.canAddMore
                        ? () => _showSourcePicker(context)
                        : null,
                    onDelete: (id) => _delete(context, id),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _PhotoGrid extends StatelessWidget {
  const _PhotoGrid({
    required this.state,
    required this.headersFuture,
    required this.onAdd,
    required this.onDelete,
  });

  final PhotoManagerState state;
  final Future<Map<String, String>> headersFuture;
  final VoidCallback? onAdd;
  final ValueChanged<int> onDelete;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    if (state.photos.isEmpty && !state.uploading) {
      return EmptyState(
        icon: Icons.photo_camera_back_outlined,
        title: 'No photos yet',
        message:
            'Add up to ${AppConstants.maxPhotosPerProperty} real photos so '
            'renters see the actual unit, not a placeholder.',
        actionLabel: 'Add a photo',
        onAction: onAdd,
      );
    }
    return FutureBuilder<Map<String, String>>(
      future: headersFuture,
      builder: (context, snapshot) {
        final headers = snapshot.data ?? const {};
        return GridView.builder(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1,
          ),
          itemCount: state.photos.length + 1,
          itemBuilder: (context, i) {
            if (i == state.photos.length) {
              return _AddTile(onTap: onAdd, uploading: state.uploading);
            }
            final photo = state.photos[i];
            return ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  NetworkPhoto(
                    url: photo.url,
                    headers: headers,
                    errorPlaceholder: ColoredBox(
                      color: c.surfaceSunken,
                      child: Icon(Icons.broken_image_outlined,
                          color: c.inkMuted),
                    ),
                  ),
                  Positioned(
                    top: 6,
                    right: 6,
                    child: Pressable(
                      onTap: () => onDelete(photo.id),
                      child: Container(
                        padding: const EdgeInsets.all(5),
                        decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.55),
                            shape: BoxShape.circle),
                        child: const Icon(Icons.close,
                            size: 15, color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

class _AddTile extends StatelessWidget {
  const _AddTile({required this.onTap, required this.uploading});
  final VoidCallback? onTap;
  final bool uploading;

  @override
  Widget build(BuildContext context) {
    final c = AppColors.of(context);
    return Pressable(
      onTap: uploading ? null : onTap,
      child: Container(
        decoration: BoxDecoration(
          color: c.surfaceSunken.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: c.border),
        ),
        child: Center(
          child: uploading
              ? SizedBox(
                  width: 28,
                  height: 28,
                  child: CircularProgressIndicator(
                      strokeWidth: 2.4, color: c.green),
                )
              : Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                        onTap == null
                            ? Icons.block
                            : Icons.add_a_photo_outlined,
                        color: onTap == null ? c.inkMuted : c.green,
                        size: 24),
                    const SizedBox(height: 6),
                    Text(onTap == null ? 'Limit reached' : 'Add photo',
                        style: AppType.caption(c, color: c.inkMuted)),
                  ],
                ),
        ),
      ),
    );
  }
}
