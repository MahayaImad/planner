import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../pages/a_venir.dart';
import '../pages/connexion.dart';
import '../pages/donnees.dart';
import '../pages/emploi_du_temps.dart';
import '../pages/saisies.dart';
import '../pages/tableau_de_bord.dart';
import '../widgets/coquille.dart';
import 'navigation.dart';
import 'session.dart';

/// Rend `go_router` sensible aux changements de session sans l'abonner
/// à Riverpod : le routeur écoute ce notifieur, qui ne s'agite qu'à la
/// connexion et à la déconnexion.
class _Sonnette extends ChangeNotifier {
  void sonner() => notifyListeners();
}

final routeurProvider = Provider<GoRouter>((ref) {
  final sonnette = _Sonnette();
  ref.listen<Session>(sessionProvider, (avant, apres) {
    if (avant?.connectee != apres.connectee ||
        avant?.pretePourDemarrer != apres.pretePourDemarrer) {
      sonnette.sonner();
    }
  });
  ref.onDispose(sonnette.dispose);

  return GoRouter(
    initialLocation: '/tableau-de-bord',
    refreshListenable: sonnette,
    redirect: (contexte, etat) {
      final session = ref.read(sessionProvider);
      // Tant que les préférences n'ont pas été relues, on ne redirige
      // pas : sinon l'écran de connexion clignote au démarrage pour un
      // utilisateur déjà authentifié.
      if (!session.pretePourDemarrer) return null;
      final surConnexion = etat.uri.path == '/connexion';
      if (!session.connectee) return surConnexion ? null : '/connexion';
      if (surConnexion) return '/tableau-de-bord';
      return null;
    },
    routes: [
      GoRoute(
        path: '/connexion',
        builder: (contexte, etat) => const PageConnexion(),
      ),
      ShellRoute(
        builder: (contexte, etat, enfant) => Coquille(enfant: enfant),
        routes: [
          GoRoute(
            path: '/tableau-de-bord',
            builder: (contexte, etat) => const PageTableauDeBord(),
          ),
          GoRoute(
            path: '/donnees',
            builder: (contexte, etat) => const PageDonnees(),
          ),
          GoRoute(
            path: '/enseignants',
            builder: (contexte, etat) => const PageEnseignants(),
          ),
          GoRoute(
            path: '/matieres',
            builder: (contexte, etat) => const PageMatieres(),
          ),
          GoRoute(
            path: '/salles',
            builder: (contexte, etat) => const PageSalles(),
          ),
          GoRoute(
            path: '/divisions',
            builder: (contexte, etat) => const PageDivisions(),
          ),
          GoRoute(
            path: '/programme',
            builder: (contexte, etat) => const PageProgramme(),
          ),
          GoRoute(
            path: '/emplois-du-temps',
            builder: (contexte, etat) => const PageEmploiDuTemps(),
          ),
          // Les écrans encore à écrire annoncent honnêtement leur état
          // plutôt que d'afficher une page blanche.
          for (final destination
              in destinations.where((d) => d.chemin == '/reglages'))
            GoRoute(
              path: destination.chemin,
              builder: (contexte, etat) =>
                  PageAVenir(destination: destination),
            ),
        ],
      ),
    ],
  );
});
