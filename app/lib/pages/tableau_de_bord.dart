import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';
import '../widgets/etats.dart';

/// Ce que contient l'établissement, et la prochaine chose à faire.
final _resumeProvider = FutureProvider.autoDispose((ref) async {
  final api = ref.watch(apiProvider);
  final reponses = await Future.wait([
    api.get('/professeurs/'),
    api.get('/matieres/'),
    api.get('/salles/'),
    api.get('/classes/'),
    api.get('/programme/'),
  ]);
  return <String, int>{
    'enseignants': (reponses[0] as List).length,
    'matieres': (reponses[1] as List).length,
    'salles': (reponses[2] as List).length,
    'divisions': (reponses[3] as List).length,
    'programme': (reponses[4] as List).length,
  };
});

class PageTableauDeBord extends ConsumerWidget {
  const PageTableauDeBord({super.key});

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    final resume = ref.watch(_resumeProvider);
    final session = ref.watch(sessionProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l.tableauDeBord),
        actions: [
          IconButton(
            tooltip: l.reessayer,
            onPressed: () => ref.invalidate(_resumeProvider),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: resume.when(
        loading: () => EtatChargement(message: l.chargement),
        error: (erreur, _) => EtatErreur(
          erreur: erreur,
          onReessayer: () => ref.invalidate(_resumeProvider),
        ),
        data: (compte) => ListView(
          padding: const EdgeInsets.all(Jetons.l),
          children: [
            if (session.nomEcole.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: Jetons.m),
                child: Text(
                  session.nomEcole,
                  style: Theme.of(contexte)
                      .textTheme
                      .headlineSmall
                      ?.copyWith(fontWeight: FontWeight.w700),
                ),
              ),
            Text(l.resumeEtablissement,
                style: Theme.of(contexte).textTheme.titleMedium),
            const SizedBox(height: Jetons.m),
            _GrilleChiffres(compte: compte),
            const SizedBox(height: Jetons.xl),
            Text(l.commencerIci,
                style: Theme.of(contexte).textTheme.titleMedium),
            const SizedBox(height: Jetons.m),
            _Etape(
              numero: 1,
              titre: l.etapeDonnees,
              aide: l.etapeDonneesAide,
              faite: compte['enseignants']! > 0 && compte['divisions']! > 0,
              onOuvrir: () => contexte.go('/donnees'),
            ),
            _Etape(
              numero: 2,
              titre: l.etapeProgramme,
              aide: l.etapeProgrammeAide,
              faite: compte['programme']! > 0,
              onOuvrir: () => contexte.go('/programme'),
            ),
            _Etape(
              numero: 3,
              titre: l.etapeGenerer,
              aide: l.etapeGenererAide,
              faite: false,
              onOuvrir: () => contexte.go('/emplois-du-temps'),
            ),
          ],
        ),
      ),
    );
  }
}

class _GrilleChiffres extends StatelessWidget {
  const _GrilleChiffres({required this.compte});

  final Map<String, int> compte;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final cartes = <({IconData icone, String texte, String chemin})>[
      (
        icone: Icons.people_outline,
        texte: l.nbEnseignants(compte['enseignants']!),
        chemin: '/enseignants'
      ),
      (
        icone: Icons.school_outlined,
        texte: l.nbDivisions(compte['divisions']!),
        chemin: '/divisions'
      ),
      (
        icone: Icons.menu_book_outlined,
        texte: l.nbMatieres(compte['matieres']!),
        chemin: '/matieres'
      ),
      (
        icone: Icons.meeting_room_outlined,
        texte: l.nbSalles(compte['salles']!),
        chemin: '/salles'
      ),
      (
        icone: Icons.list_alt_outlined,
        texte: l.nbLignesProgramme(compte['programme']!),
        chemin: '/programme'
      ),
    ];

    // Le nombre de colonnes suit la largeur disponible plutôt qu'un
    // point de rupture fixe : la grille tient aussi bien dans un volet
    // étroit que sur un écran de bureau.
    return LayoutBuilder(
      builder: (contexte, contraintes) {
        final colonnes = (contraintes.maxWidth / 220).floor().clamp(1, 5);
        return GridView.count(
          crossAxisCount: colonnes,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: Jetons.m,
          crossAxisSpacing: Jetons.m,
          childAspectRatio: 2.2,
          children: [
            for (final carte in cartes)
              _CarteChiffre(
                icone: carte.icone,
                texte: carte.texte,
                onOuvrir: () => contexte.go(carte.chemin),
              ),
          ],
        );
      },
    );
  }
}

class _CarteChiffre extends StatelessWidget {
  const _CarteChiffre({
    required this.icone,
    required this.texte,
    required this.onOuvrir,
  });

  final IconData icone;
  final String texte;
  final VoidCallback onOuvrir;

  @override
  Widget build(BuildContext contexte) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onOuvrir,
        child: Padding(
          padding: const EdgeInsets.all(Jetons.m),
          child: Row(
            children: [
              Icon(icone, color: Jetons.primaire),
              const SizedBox(width: Jetons.s),
              Expanded(
                child: Text(
                  texte,
                  style: Theme.of(contexte)
                      .textTheme
                      .titleSmall
                      ?.copyWith(fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Etape extends StatelessWidget {
  const _Etape({
    required this.numero,
    required this.titre,
    required this.aide,
    required this.faite,
    required this.onOuvrir,
  });

  final int numero;
  final String titre;
  final String aide;
  final bool faite;
  final VoidCallback onOuvrir;

  @override
  Widget build(BuildContext contexte) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Jetons.m),
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onOuvrir,
          child: Padding(
            padding: const EdgeInsets.all(Jetons.m),
            child: Row(
              children: [
                // L'état « fait » se lit à la fois par l'icône et par
                // sa forme, jamais par la seule couleur.
                CircleAvatar(
                  radius: 16,
                  backgroundColor:
                      faite ? Jetons.succes : Jetons.attenue,
                  child: faite
                      ? const Icon(Icons.check,
                          size: 18, color: Colors.white)
                      : Text('$numero',
                          style: const TextStyle(
                              fontWeight: FontWeight.w700,
                              color: Jetons.encre)),
                ),
                const SizedBox(width: Jetons.m),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(titre,
                          style: Theme.of(contexte)
                              .textTheme
                              .titleSmall
                              ?.copyWith(fontWeight: FontWeight.w600)),
                      Text(aide,
                          style: Theme.of(contexte)
                              .textTheme
                              .bodySmall
                              ?.copyWith(color: Jetons.encreAttenuee)),
                    ],
                  ),
                ),
                Icon(
                  contexte.estRtl
                      ? Icons.chevron_left
                      : Icons.chevron_right,
                  color: Jetons.encreAttenuee,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
