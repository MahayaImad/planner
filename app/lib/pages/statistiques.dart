import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';
import '../widgets/etats.dart';

final _statsProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>, int>((ref, edtId) async {
  return await ref.watch(apiProvider).get(
      '/emplois-du-temps/$edtId/statistiques') as Map<String, dynamic>;
});

/// Ce que l'emploi du temps est devenu : service de chaque enseignant,
/// charge des divisions, occupation des séances.
///
/// Recalculé par le serveur à la lecture, donc juste même après des
/// retouches manuelles.
class PageStatistiques extends ConsumerWidget {
  const PageStatistiques({super.key, required this.edtId});

  final int edtId;

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    final stats = ref.watch(_statsProvider(edtId));

    return Scaffold(
      appBar: AppBar(title: Text(l.statistiques)),
      body: stats.when(
        loading: () => EtatChargement(message: l.chargement),
        error: (erreur, _) => EtatErreur(
            erreur: erreur,
            onReessayer: () => ref.invalidate(_statsProvider(edtId))),
        data: (donnees) => _Contenu(donnees: donnees),
      ),
    );
  }
}

class _Contenu extends StatelessWidget {
  const _Contenu({required this.donnees});

  final Map<String, dynamic> donnees;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final totaux = donnees['totaux'] as Map<String, dynamic>;
    final resume = donnees['resume'] as Map<String, dynamic>;
    final professeurs = (donnees['professeurs'] as List).cast<Map>();
    final classes = (donnees['classes'] as List).cast<Map>();
    final seances = (donnees['occupation_seances'] as List).cast<Map>();

    final charges = (resume['charges_quotidiennes'] as Map?) ?? const {};
    final lourdes = charges.entries
        .where((e) => (int.tryParse('${e.key}') ?? 0) >= 6)
        .fold<int>(0, (total, e) => total + (e.value as int));

    return ListView(
      padding: const EdgeInsets.all(Jetons.l),
      children: [
        Wrap(
          spacing: Jetons.m,
          runSpacing: Jetons.m,
          children: [
            _Chiffre(
                valeur: '${totaux['lecons']}', libelle: l.heuresPlacees),
            _Chiffre(
                valeur: '${resume['trous_classes']}',
                libelle: l.trousElevesCourt,
                alerte: (resume['trous_classes'] as int) > 0),
            _Chiffre(
                valeur: '${resume['trous_professeurs']}',
                libelle: l.trousProfesseursCourt),
            _Chiffre(
                valeur: '${resume['demi_journees_isolees']}',
                libelle: l.demiJourneesIsolees),
            _Chiffre(
                valeur: '$lourdes',
                libelle: l.journeesSixHeures,
                alerte: lourdes > 0),
            _Chiffre(
                valeur: '${resume['matieres_a_trois_heures']}',
                libelle: l.matieresTroisHeures,
                alerte: (resume['matieres_a_trois_heures'] as int) > 0),
          ],
        ),
        const SizedBox(height: Jetons.xl),
        Text(l.occupationSeances,
            style: Theme.of(contexte).textTheme.titleMedium),
        const SizedBox(height: Jetons.m),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(Jetons.m),
            child: Column(
              children: [
                for (final seance in seances)
                  _LigneOccupation(seance: seance),
              ],
            ),
          ),
        ),
        const SizedBox(height: Jetons.xl),
        Text(l.serviceDesProfesseurs,
            style: Theme.of(contexte).textTheme.titleMedium),
        const SizedBox(height: Jetons.m),
        _Tableau(
          entetes: [l.nom, l.heures, l.jours, l.trous, l.maxJour],
          lignes: [
            for (final professeur in professeurs)
              [
                '${professeur['nom']}',
                '${professeur['heures']}',
                '${professeur['jours_presence']}',
                '${professeur['trous']}',
                '${professeur['charge_max']} h',
              ],
          ],
          alerte: (ligne) =>
              int.tryParse(ligne[4].split(' ').first) != null &&
              int.parse(ligne[4].split(' ').first) >= 6,
        ),
        const SizedBox(height: Jetons.xl),
        Text(l.chargeDesDivisions,
            style: Theme.of(contexte).textTheme.titleMedium),
        const SizedBox(height: Jetons.m),
        _Tableau(
          entetes: [l.nom, l.heures, l.trous, l.journeeLaPlusChargee,
              l.matieresTroisHeures],
          lignes: [
            for (final division in classes)
              [
                '${division['nom']}',
                '${division['heures']}',
                '${division['trous']}',
                '${division['charge_max']} h',
                '${division['matieres_a_trois_heures']}',
              ],
          ],
          alerte: (ligne) => ligne[2] != '0',
        ),
      ],
    );
  }
}

class _Chiffre extends StatelessWidget {
  const _Chiffre({
    required this.valeur,
    required this.libelle,
    this.alerte = false,
  });

  final String valeur;
  final String libelle;
  final bool alerte;

  @override
  Widget build(BuildContext contexte) => Card(
        child: Container(
          width: 168,
          padding: const EdgeInsets.all(Jetons.m),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(valeur,
                  style: Theme.of(contexte).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        color: alerte ? Jetons.alerte : Jetons.encre,
                      )),
              Text(libelle,
                  style: Theme.of(contexte)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: Jetons.encreAttenuee)),
            ],
          ),
        ),
      );
}

class _LigneOccupation extends StatelessWidget {
  const _LigneOccupation({required this.seance});

  final Map seance;

  @override
  Widget build(BuildContext contexte) {
    final possible = seance['possible'] as int;
    final occupe = seance['occupe'] as int;
    final taux = possible == 0 ? 0.0 : occupe / possible;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: Jetons.xs),
      child: Row(
        children: [
          SizedBox(
            width: 112,
            child: Text('${seance['debut']} – ${seance['fin']}',
                style: Theme.of(contexte).textTheme.bodySmall),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: taux,
                minHeight: 8,
                backgroundColor: Jetons.attenue,
              ),
            ),
          ),
          SizedBox(
            width: 96,
            child: Text('$occupe / $possible',
                textAlign: TextAlign.end,
                style: Theme.of(contexte).textTheme.bodySmall),
          ),
        ],
      ),
    );
  }
}

/// Un tableau qui défile horizontalement plutôt que de comprimer ses
/// colonnes jusqu'à l'illisible sur téléphone.
class _Tableau extends StatelessWidget {
  const _Tableau({
    required this.entetes,
    required this.lignes,
    this.alerte,
  });

  final List<String> entetes;
  final List<List<String>> lignes;
  final bool Function(List<String>)? alerte;

  @override
  Widget build(BuildContext contexte) => Card(
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: [
              for (final entete in entetes)
                DataColumn(
                    label: Text(entete,
                        style: const TextStyle(fontWeight: FontWeight.w700))),
            ],
            rows: [
              for (final ligne in lignes)
                DataRow(
                  cells: [
                    for (var i = 0; i < ligne.length; i++)
                      DataCell(Text(
                        ligne[i],
                        style: TextStyle(
                          color: (alerte?.call(ligne) ?? false) && i > 0
                              ? Jetons.alerte
                              : null,
                        ),
                      )),
                  ],
                ),
            ],
          ),
        ),
      );
}
