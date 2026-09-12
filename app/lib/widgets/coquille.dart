import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/navigation.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';

/// Charpente commune : navigation à gauche sur grand écran, en bas sur
/// téléphone.
///
/// Un seul jeu de destinations sert les deux formats. La barre du bas
/// n'en montre que quatre — au-delà de cinq, les libellés se tronquent
/// et la zone tactile passe sous le seuil confortable ; le reste est
/// derrière « Plus ».
class Coquille extends ConsumerWidget {
  const Coquille({super.key, required this.enfant});

  final Widget enfant;

  static const _seuilRail = 720.0;
  static const _seuilRailEtendu = 1180.0;

  int _indexCourant(BuildContext contexte) {
    final chemin = GoRouterState.of(contexte).uri.path;
    final index = destinations.indexWhere(
        (d) => chemin == d.chemin || chemin.startsWith('${d.chemin}/'));
    return index < 0 ? 0 : index;
  }

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    final index = _indexCourant(contexte);

    return LayoutBuilder(
      builder: (contexte, contraintes) {
        final large = contraintes.maxWidth >= _seuilRail;
        if (large) {
          return Scaffold(
            body: Row(
              children: [
                _Rail(
                  index: index,
                  etendu: contraintes.maxWidth >= _seuilRailEtendu,
                ),
                const VerticalDivider(width: 1),
                Expanded(child: enfant),
              ],
            ),
          );
        }
        final principales =
            destinations.where((d) => d.principale).toList(growable: false);
        final indexPrincipal = principales.indexWhere(
            (d) => d.chemin == destinations[index].chemin);
        return Scaffold(
          body: enfant,
          bottomNavigationBar: NavigationBar(
            selectedIndex: indexPrincipal < 0 ? 0 : indexPrincipal,
            onDestinationSelected: (i) {
              if (i == principales.length) {
                _ouvrirPlus(contexte);
              } else {
                contexte.go(principales[i].chemin);
              }
            },
            destinations: [
              for (final destination in principales)
                NavigationDestination(
                  icon: Icon(destination.icone),
                  selectedIcon: Icon(destination.iconeActive),
                  label: destination.libelle(l),
                  tooltip: destination.libelle(l),
                ),
              NavigationDestination(
                icon: const Icon(Icons.more_horiz),
                label: l.plus,
                tooltip: l.plus,
              ),
            ],
          ),
        );
      },
    );
  }

  void _ouvrirPlus(BuildContext contexte) {
    final l = contexte.l10n;
    showModalBottomSheet<void>(
      context: contexte,
      showDragHandle: true,
      builder: (feuille) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (final destination
                in destinations.where((d) => !d.principale))
              ListTile(
                leading: Icon(destination.icone),
                title: Text(destination.libelle(l)),
                onTap: () {
                  Navigator.of(feuille).pop();
                  contexte.go(destination.chemin);
                },
              ),
            const Divider(),
            const _ChoixLangue(),
            const _BoutonDeconnexion(),
          ],
        ),
      ),
    );
  }
}

class _Rail extends ConsumerWidget {
  const _Rail({required this.index, required this.etendu});

  final int index;
  final bool etendu;

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    final session = ref.watch(sessionProvider);
    return SingleChildScrollView(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          minHeight: MediaQuery.sizeOf(contexte).height,
        ),
        child: IntrinsicHeight(
          child: NavigationRail(
            extended: etendu,
            selectedIndex: index,
            onDestinationSelected: (i) => contexte.go(destinations[i].chemin),
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: Jetons.m),
              child: etendu
                  ? Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: Jetons.m),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(l.appNom,
                              style: Theme.of(contexte)
                                  .textTheme
                                  .titleMedium
                                  ?.copyWith(fontWeight: FontWeight.w700)),
                          if (session.nomEcole.isNotEmpty)
                            Text(session.nomEcole,
                                style: Theme.of(contexte)
                                    .textTheme
                                    .bodySmall
                                    ?.copyWith(
                                        color: Jetons.encreAttenuee)),
                        ],
                      ),
                    )
                  : const Icon(Icons.schedule, color: Jetons.primaire),
            ),
            trailing: const Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: Padding(
                  padding: EdgeInsets.only(bottom: Jetons.m),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [_ChoixLangue(compact: true), _BoutonDeconnexion(compact: true)],
                  ),
                ),
              ),
            ),
            destinations: [
              for (final destination in destinations)
                NavigationRailDestination(
                  icon: Icon(destination.icone),
                  selectedIcon: Icon(destination.iconeActive),
                  label: Text(destination.libelle(l)),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ChoixLangue extends ConsumerWidget {
  const _ChoixLangue({this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    final courante = Localizations.localeOf(contexte).languageCode;
    void basculer() {
      ref.read(langueProvider.notifier).choisir(
          Locale(courante == 'ar' ? 'fr' : 'ar'));
    }

    if (compact) {
      return IconButton(
        onPressed: basculer,
        tooltip: l.langue,
        icon: const Icon(Icons.translate),
      );
    }
    return ListTile(
      leading: const Icon(Icons.translate),
      title: Text(l.langue),
      trailing: Text(courante == 'ar' ? l.francais : l.arabe),
      onTap: basculer,
    );
  }
}

class _BoutonDeconnexion extends ConsumerWidget {
  const _BoutonDeconnexion({this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    Future<void> partir() async {
      await ref.read(sessionProvider.notifier).deconnecter();
      if (contexte.mounted) contexte.go('/connexion');
    }

    if (compact) {
      return IconButton(
        onPressed: partir,
        tooltip: l.seDeconnecter,
        icon: const Icon(Icons.logout),
      );
    }
    return ListTile(
      leading: const Icon(Icons.logout),
      title: Text(l.seDeconnecter),
      onTap: partir,
    );
  }
}
