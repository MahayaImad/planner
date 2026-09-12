import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api.dart';
import '../core/ressources.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';
import '../widgets/etats.dart';

final _reglagesProvider = FutureProvider.autoDispose((ref) async {
  final api = ref.watch(apiProvider);
  final reponses = await Future.wait([
    api.get('/parametres'),
    api.get('/fenetres-pedagogiques'),
  ]);
  return (
    parametres: reponses[0] as Map<String, dynamic>,
    fenetres: (reponses[1] as List).cast<Map<String, dynamic>>(),
  );
});

/// Les critères souples, avec ce que chacun arbitre.
///
/// Le libellé seul ne suffit pas : « journée hachée » ne dit rien à qui
/// ne connaît pas le solveur. L'aide dit ce que le poids achète et ce
/// qu'il coûte.
const _criteres = <({String cle, String Function(L) titre, String Function(L) aide})>[
  (cle: 'trous_professeurs', titre: _t1, aide: _a1),
  (cle: 'trous_doubles_professeurs', titre: _t2, aide: _a2),
  (cle: 'journee_hachee_professeur', titre: _t3, aide: _a3),
  (cle: 'heure_isolee_professeur', titre: _t4, aide: _a4),
  (cle: 'jours_presence_professeurs', titre: _t5, aide: _a5),
  (cle: 'recompense_permanence', titre: _t6, aide: _a6),
  (cle: 'blocs_hors_politique', titre: _t7, aide: _a7),
  (cle: 'matieres_repetees_par_jour', titre: _t8, aide: _a8),
  (cle: 'equite_derniere_seance', titre: _t9, aide: _a9),
  (cle: 'equilibrage_charge_classes', titre: _t10, aide: _a10),
  (cle: 'demi_journees_travaillees_classes', titre: _t11, aide: _a11),
  (cle: 'matieres_lourdes_apres_midi', titre: _t12, aide: _a12),
];

String _t1(L l) => l.critereTrousProfesseurs;
String _a1(L l) => l.aideTrousProfesseurs;
String _t2(L l) => l.critereVideDeuxHeures;
String _a2(L l) => l.aideVideDeuxHeures;
String _t3(L l) => l.critereJourneeHachee;
String _a3(L l) => l.aideJourneeHachee;
String _t4(L l) => l.critereHeureIsolee;
String _a4(L l) => l.aideHeureIsolee;
String _t5(L l) => l.critereJourPresence;
String _a5(L l) => l.aideJourPresence;
String _t6(L l) => l.criterePermanence;
String _a6(L l) => l.aidePermanenceCritere;
String _t7(L l) => l.critereBlocsHorsPolitique;
String _a7(L l) => l.aideBlocsHorsPolitique;
String _t8(L l) => l.critereMatieresRepetees;
String _a8(L l) => l.aideMatieresRepetees;
String _t9(L l) => l.critereEquiteFins;
String _a9(L l) => l.aideEquiteFins;
String _t10(L l) => l.critereEquilibreJournees;
String _a10(L l) => l.aideEquilibreJournees;
String _t11(L l) => l.critereDemiJournees;
String _a11(L l) => l.aideDemiJournees;
String _t12(L l) => l.critereMatieresLourdes;
String _a12(L l) => l.aideMatieresLourdes;

class PageReglages extends ConsumerStatefulWidget {
  const PageReglages({super.key});

  @override
  ConsumerState<PageReglages> createState() => _PageReglagesState();
}

class _PageReglagesState extends ConsumerState<PageReglages> {
  Map<String, dynamic>? _brouillon;
  bool _enCours = false;
  bool _modifie = false;

  Map<String, dynamic> get _grille =>
      _brouillon!['grille'] as Map<String, dynamic>;
  Map<String, dynamic> get _poids =>
      _brouillon!['ponderations'] as Map<String, dynamic>;

  void _toucher(VoidCallback modification) {
    setState(() {
      modification();
      _modifie = true;
    });
  }

  Future<void> _enregistrer() async {
    setState(() => _enCours = true);
    final l = context.l10n;
    try {
      await ref.read(apiProvider).put('/parametres', corps: {
        'grille': _grille,
        'ponderations': _poids,
        'presence_minimale': _brouillon!['presence_minimale'],
        'type_salle_ordinaire': _brouillon!['type_salle_ordinaire'],
        'limite_secondes': _brouillon!['limite_secondes'],
      });
      if (mounted) {
        setState(() => _modifie = false);
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l.reglagesEnregistres)));
      }
      ref.invalidate(_reglagesProvider);
    } on ErreurApi catch (erreur) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          backgroundColor: Jetons.danger,
          content: Text(erreur.reseau ? l.erreurReseau : erreur.message),
        ));
      }
    } finally {
      if (mounted) setState(() => _enCours = false);
    }
  }

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final reglages = ref.watch(_reglagesProvider);

    return reglages.when(
      loading: () => Scaffold(
        appBar: AppBar(title: Text(l.reglages)),
        body: EtatChargement(message: l.chargement),
      ),
      error: (erreur, _) => Scaffold(
        appBar: AppBar(title: Text(l.reglages)),
        body: EtatErreur(
            erreur: erreur,
            onReessayer: () => ref.invalidate(_reglagesProvider)),
      ),
      data: (donnees) {
        // Le brouillon est une copie : on ne modifie rien tant que
        // l'utilisateur n'a pas enregistré.
        _brouillon ??= {
          ...donnees.parametres,
          'grille': {
            ...donnees.parametres['grille'] as Map<String, dynamic>,
            'jours': List<String>.from(
                (donnees.parametres['grille'] as Map)['jours'] as List),
            'horaires': [
              for (final h in (donnees.parametres['grille'] as Map)['horaires']
                  as List)
                List<String>.from((h as List).map((x) => '$x')),
            ],
            'fermetures': [
              for (final f in ((donnees.parametres['grille'] as Map)['fermetures']
                      as List? ??
                  const []))
                [(f as List)[0], List<int>.from(f[1] as List)],
            ],
          },
          'ponderations':
              Map<String, dynamic>.from(donnees.parametres['ponderations'] as Map),
        };

        return DefaultTabController(
          length: 3,
          child: Scaffold(
            appBar: AppBar(
              title: Text(l.reglages),
              bottom: TabBar(
                isScrollable: true,
                tabs: [
                  Tab(text: l.ongletGrille),
                  Tab(text: l.ongletCriteres),
                  Tab(text: l.ongletFenetres),
                ],
              ),
              actions: [
                if (_modifie)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: Jetons.s),
                    child: FilledButton.icon(
                      onPressed: _enCours ? null : _enregistrer,
                      icon: const Icon(Icons.save_outlined),
                      label: Text(l.enregistrer),
                    ),
                  ),
              ],
            ),
            body: TabBarView(
              children: [
                _OngletGrille(
                  grille: _grille,
                  parametres: _brouillon!,
                  onModifier: _toucher,
                ),
                _OngletCriteres(poids: _poids, onModifier: _toucher),
                _OngletFenetres(fenetres: donnees.fenetres),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _OngletGrille extends StatelessWidget {
  const _OngletGrille({
    required this.grille,
    required this.parametres,
    required this.onModifier,
  });

  final Map<String, dynamic> grille;
  final Map<String, dynamic> parametres;
  final void Function(VoidCallback) onModifier;

  bool _fermee(int jour, int seance) {
    for (final fermeture in grille['fermetures'] as List) {
      if ((fermeture as List)[0] == jour &&
          (fermeture[1] as List).contains(seance)) {
        return true;
      }
    }
    return false;
  }

  void _basculer(int jour, int seance) {
    final fermetures = grille['fermetures'] as List;
    for (final fermeture in fermetures) {
      if ((fermeture as List)[0] == jour) {
        final seances = fermeture[1] as List;
        seances.contains(seance)
            ? seances.remove(seance)
            : seances.add(seance);
        if (seances.isEmpty) fermetures.remove(fermeture);
        return;
      }
    }
    fermetures.add([jour, <int>[seance]]);
  }

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final jours = (grille['jours'] as List).cast<String>();
    final horaires = (grille['horaires'] as List).cast<List>();

    return ListView(
      padding: const EdgeInsets.all(Jetons.l),
      children: [
        Text(l.fermeturesTitre,
            style: Theme.of(contexte).textTheme.titleMedium),
        const SizedBox(height: Jetons.xs),
        Text(l.fermeturesAide,
            style: Theme.of(contexte)
                .textTheme
                .bodySmall
                ?.copyWith(color: Jetons.encreAttenuee)),
        const SizedBox(height: Jetons.m),
        Card(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: [
                const DataColumn(label: Text('')),
                for (final jour in jours) DataColumn(label: Text(jour)),
              ],
              rows: [
                for (var seance = 0; seance < horaires.length; seance++)
                  DataRow(cells: [
                    DataCell(Text('${horaires[seance][0]}',
                        style:
                            const TextStyle(fontWeight: FontWeight.w600))),
                    for (var jour = 0; jour < jours.length; jour++)
                      DataCell(
                        // Coché = ouvert. Dire « fermé » par une case
                        // vide se lit mieux qu'une case cochée qui
                        // voudrait dire « interdit ».
                        Checkbox(
                          value: !_fermee(jour, seance),
                          onChanged: (_) =>
                              onModifier(() => _basculer(jour, seance)),
                        ),
                      ),
                  ]),
              ],
            ),
          ),
        ),
        const SizedBox(height: Jetons.xl),
        Text(l.horairesTitre, style: Theme.of(contexte).textTheme.titleMedium),
        const SizedBox(height: Jetons.m),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(Jetons.m),
            child: Column(
              children: [
                for (var i = 0; i < horaires.length; i++)
                  Padding(
                    padding: const EdgeInsets.only(bottom: Jetons.s),
                    child: Row(
                      children: [
                        SizedBox(
                            width: 44,
                            child: Text('S${i + 1}',
                                style: const TextStyle(
                                    fontWeight: FontWeight.w600))),
                        Expanded(
                          child: TextFormField(
                            initialValue: '${horaires[i][0]}',
                            decoration:
                                InputDecoration(labelText: l.debut, isDense: true),
                            onChanged: (valeur) =>
                                onModifier(() => horaires[i][0] = valeur),
                          ),
                        ),
                        const SizedBox(width: Jetons.s),
                        Expanded(
                          child: TextFormField(
                            initialValue: '${horaires[i][1]}',
                            decoration:
                                InputDecoration(labelText: l.fin, isDense: true),
                            onChanged: (valeur) =>
                                onModifier(() => horaires[i][1] = valeur),
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: Jetons.xl),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(Jetons.m),
            child: Column(
              children: [
                TextFormField(
                  initialValue: '${parametres['limite_secondes']}',
                  decoration: InputDecoration(
                      labelText: l.tempsDeCalculDefaut,
                      helperText: l.aideTempsDefaut),
                  keyboardType: TextInputType.number,
                  onChanged: (valeur) => onModifier(() =>
                      parametres['limite_secondes'] =
                          int.tryParse(valeur) ?? parametres['limite_secondes']),
                ),
                const SizedBox(height: Jetons.m),
                TextFormField(
                  initialValue: '${parametres['type_salle_ordinaire']}',
                  decoration: InputDecoration(
                      labelText: l.typeSalleOrdinaire,
                      helperText: l.aideTypeSalleOrdinaire),
                  onChanged: (valeur) => onModifier(
                      () => parametres['type_salle_ordinaire'] = valeur),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _OngletCriteres extends StatelessWidget {
  const _OngletCriteres({required this.poids, required this.onModifier});

  final Map<String, dynamic> poids;
  final void Function(VoidCallback) onModifier;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return ListView(
      padding: const EdgeInsets.all(Jetons.l),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(Jetons.m),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: Jetons.primaire),
                const SizedBox(width: Jetons.s),
                Expanded(
                    child: Text(l.criteresAide,
                        style: Theme.of(contexte).textTheme.bodySmall)),
              ],
            ),
          ),
        ),
        const SizedBox(height: Jetons.l),
        for (final critere in _criteres)
          _Curseur(
            titre: critere.titre(l),
            aide: critere.aide(l),
            valeur: (poids[critere.cle] as num?)?.toInt() ?? 0,
            onChange: (valeur) =>
                onModifier(() => poids[critere.cle] = valeur),
          ),
        const SizedBox(height: Jetons.l),
        _GrilleSeuils(
          titre: l.seuilsSeanceTitre,
          aide: l.seuilsSeanceAide,
          valeurs: (poids['penalites_seance'] as Map?) ?? {},
          cles: const ['0', '1', '2', '3', '4', '5', '6'],
          etiquette: (cle) => 'S${int.parse(cle) + 1}',
          onChange: (cle, valeur) => onModifier(() {
            poids['penalites_seance'] = {
              ...((poids['penalites_seance'] as Map?) ?? {}),
              cle: valeur,
            };
          }),
        ),
        const SizedBox(height: Jetons.l),
        _GrilleSeuils(
          titre: l.seuilsChargeTitre,
          aide: l.seuilsChargeAide,
          valeurs: (poids['penalites_heures_par_jour'] as Map?) ?? {},
          cles: const ['3', '4', '5', '6', '7'],
          etiquette: (cle) => '$cle h',
          onChange: (cle, valeur) => onModifier(() {
            poids['penalites_heures_par_jour'] = {
              ...((poids['penalites_heures_par_jour'] as Map?) ?? {}),
              cle: valeur,
            };
          }),
        ),
      ],
    );
  }
}

class _Curseur extends StatelessWidget {
  const _Curseur({
    required this.titre,
    required this.aide,
    required this.valeur,
    required this.onChange,
  });

  final String titre;
  final String aide;
  final int valeur;
  final ValueChanged<int> onChange;

  @override
  Widget build(BuildContext contexte) => Padding(
        padding: const EdgeInsets.only(bottom: Jetons.m),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(titre,
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                ),
                Chip(label: Text('$valeur')),
              ],
            ),
            Text(aide,
                style: Theme.of(contexte)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: Jetons.encreAttenuee)),
            Slider(
              value: valeur.toDouble().clamp(0, 150),
              min: 0,
              max: 150,
              divisions: 30,
              label: '$valeur',
              onChanged: (nouvelle) => onChange(nouvelle.round()),
            ),
          ],
        ),
      );
}

class _GrilleSeuils extends StatelessWidget {
  const _GrilleSeuils({
    required this.titre,
    required this.aide,
    required this.valeurs,
    required this.cles,
    required this.etiquette,
    required this.onChange,
  });

  final String titre;
  final String aide;
  final Map valeurs;
  final List<String> cles;
  final String Function(String) etiquette;
  final void Function(String, int) onChange;

  @override
  Widget build(BuildContext contexte) => Card(
        child: Padding(
          padding: const EdgeInsets.all(Jetons.m),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(titre, style: const TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: Jetons.xs),
              Text(aide,
                  style: Theme.of(contexte)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: Jetons.encreAttenuee)),
              const SizedBox(height: Jetons.m),
              Wrap(
                spacing: Jetons.s,
                runSpacing: Jetons.s,
                children: [
                  for (final cle in cles)
                    SizedBox(
                      width: 108,
                      child: TextFormField(
                        initialValue: '${valeurs[cle] ?? 0}',
                        decoration: InputDecoration(
                            labelText: etiquette(cle), isDense: true),
                        keyboardType: TextInputType.number,
                        onChanged: (valeur) =>
                            onChange(cle, int.tryParse(valeur) ?? 0),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      );
}

class _OngletFenetres extends ConsumerWidget {
  const _OngletFenetres({required this.fenetres});

  final List<Map<String, dynamic>> fenetres;

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final l = contexte.l10n;
    return ListView(
      padding: const EdgeInsets.all(Jetons.l),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(Jetons.m),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: Jetons.primaire),
                const SizedBox(width: Jetons.s),
                Expanded(
                    child: Text(l.fenetresAide,
                        style: Theme.of(contexte).textTheme.bodySmall)),
              ],
            ),
          ),
        ),
        const SizedBox(height: Jetons.l),
        if (fenetres.isEmpty)
          Padding(
            padding: const EdgeInsets.all(Jetons.l),
            child: Text(l.aucuneFenetre,
                style: Theme.of(contexte)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: Jetons.encreAttenuee)),
          )
        else
          for (final fenetre in fenetres)
            Card(
              margin: const EdgeInsets.only(bottom: Jetons.s),
              child: ListTile(
                leading: const Icon(Icons.block_outlined),
                title: Text('${fenetre['matiere_nom']}'),
                subtitle: Text(l.fenetreDetail(
                    '${fenetre['index_jour']}',
                    (fenetre['seances_bloquees'] as List)
                        .map((s) => 'S${(s as int) + 1}')
                        .join(', '))),
                trailing: IconButton(
                  tooltip: l.supprimer,
                  icon: const Icon(Icons.delete_outline, color: Jetons.danger),
                  onPressed: () async {
                    await ref
                        .read(apiProvider)
                        .delete('/fenetres-pedagogiques/${fenetre['id']}');
                    ref.invalidate(_reglagesProvider);
                    ref.invalidate(collectionProvider(ressourceMatieres));
                  },
                ),
              ),
            ),
      ],
    );
  }
}
