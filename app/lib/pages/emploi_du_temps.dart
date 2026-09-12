import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api.dart';
import '../core/emploi_du_temps.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';
import '../widgets/etats.dart';

/// Angle de lecture de la grille.
enum Vue { division, enseignant, salle }

/// Le plateau : la grille de la semaine, et le glisser-déposer.
///
/// Le serveur dit lui-même quelles cases acceptent la leçon que l'on
/// soulève — il répond en quelques dizaines de millisecondes, ce qui
/// permet d'éclairer la grille pendant le geste plutôt que de refuser
/// après coup. Un déplacement refusé n'est jamais une surprise.
class PageEmploiDuTemps extends ConsumerStatefulWidget {
  const PageEmploiDuTemps({super.key});

  @override
  ConsumerState<PageEmploiDuTemps> createState() => _PageEmploiDuTempsState();
}

class _PageEmploiDuTempsState extends ConsumerState<PageEmploiDuTemps> {
  int? _edtId;
  Vue _vue = Vue.division;
  int? _filtre;

  /// Verdicts du serveur pour la leçon en cours de déplacement.
  Map<(String, String), Verdict>? _verdicts;
  int? _leconSoulevee;
  bool _enCours = false;

  Future<void> _commencerGlissement(Lecon lecon) async {
    setState(() {
      _leconSoulevee = lecon.id;
      _verdicts = null;
    });
    try {
      final verdicts = await creneauxPossibles(
          ref.read(apiProvider), _edtId!, lecon.id);
      if (mounted && _leconSoulevee == lecon.id) {
        setState(() => _verdicts = verdicts);
      }
    } on ErreurApi {
      // Sans verdicts, la grille reste neutre : le serveur revalidera
      // de toute façon au dépôt.
    }
  }

  void _finirGlissement() {
    setState(() {
      _leconSoulevee = null;
      _verdicts = null;
    });
  }

  Future<void> _deposer(Lecon lecon, String jour, String heure) async {
    setState(() => _enCours = true);
    final l = context.l10n;
    try {
      await deplacerLecon(ref.read(apiProvider), _edtId!, lecon.id, jour, heure);
      ref.invalidate(edtProvider(_edtId!));
    } on ErreurApi catch (erreur) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          backgroundColor: Jetons.danger,
          content: Text(erreur.reseau
              ? l.erreurReseau
              : _motif(l, erreur.message)),
        ));
      }
    } finally {
      if (mounted) setState(() => _enCours = false);
    }
  }

  /// Les motifs viennent du serveur sous forme de codes : la phrase est
  /// écrite ici, donc traduite comme le reste de l'interface.
  String _motif(L l, String code) => switch (code) {
        'seance_fermee' => l.motifSeanceFermee,
        'professeur_occupe' => l.motifProfesseurOccupe,
        'professeur_indisponible' => l.motifProfesseurIndisponible,
        'division_occupee' => l.motifDivisionOccupee,
        'aucune_salle_libre' => l.motifAucuneSalle,
        'fenetre_pedagogique' => l.motifFenetre,
        'plafond_journalier_professeur' => l.motifPlafondProfesseur,
        'plafond_journalier_division' => l.motifPlafondDivision,
        'plafond_journalier_matiere' => l.motifPlafondMatiere,
        'trop_heures_consecutives' => l.motifConsecutives,
        _ => code,
      };

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final liste = ref.watch(listeEdtProvider);

    return liste.when(
      loading: () => Scaffold(
        appBar: AppBar(title: Text(l.emploisDuTemps)),
        body: EtatChargement(message: l.chargement),
      ),
      error: (erreur, _) => Scaffold(
        appBar: AppBar(title: Text(l.emploisDuTemps)),
        body: EtatErreur(
            erreur: erreur, onReessayer: () => ref.invalidate(listeEdtProvider)),
      ),
      data: (emplois) {
        if (emplois.isEmpty) {
          return Scaffold(
            appBar: AppBar(title: Text(l.emploisDuTemps)),
            body: EtatVide(
              icone: Icons.calendar_month_outlined,
              titre: l.aucunEmploiDuTemps,
              aide: l.aideAucunEmploiDuTemps,
            ),
          );
        }
        _edtId ??= emplois.first['id'] as int;
        return _construireGrille(contexte, emplois);
      },
    );
  }

  Widget _construireGrille(
      BuildContext contexte, List<Map<String, dynamic>> emplois) {
    final l = contexte.l10n;
    final contenu = ref.watch(edtProvider(_edtId!));

    return Scaffold(
      appBar: AppBar(
        title: Text(l.emploisDuTemps),
        actions: [
          IconButton(
            tooltip: l.reessayer,
            onPressed: () => ref.invalidate(edtProvider(_edtId!)),
            icon: const Icon(Icons.refresh),
          ),
        ],
        bottom: _enCours
            ? const PreferredSize(
                preferredSize: Size.fromHeight(2),
                child: LinearProgressIndicator(minHeight: 2))
            : null,
      ),
      body: contenu.when(
        loading: () => EtatChargement(message: l.chargement),
        error: (erreur, _) => EtatErreur(
            erreur: erreur,
            onReessayer: () => ref.invalidate(edtProvider(_edtId!))),
        data: (donnees) {
          if (donnees.lecons.isEmpty) {
            return EtatVide(
              icone: Icons.calendar_month_outlined,
              titre: l.aucuneLecon,
              aide: l.aideAucuneLecon,
            );
          }
          final entites = _entites(donnees);
          _filtre ??= entites.isEmpty ? null : entites.first.$1;
          return Column(
            children: [
              _BarreFiltres(
                vue: _vue,
                filtre: _filtre,
                entites: entites,
                onVue: (vue) => setState(() {
                  _vue = vue;
                  _filtre = null;
                }),
                onFiltre: (valeur) => setState(() => _filtre = valeur),
              ),
              if (_leconSoulevee != null && _verdicts == null)
                LinearProgressIndicator(
                  minHeight: 2,
                  backgroundColor: Jetons.attenue,
                  color: Jetons.secondaire,
                ),
              Expanded(child: _Plateau(
                donnees: donnees,
                vue: _vue,
                filtre: _filtre,
                verdicts: _verdicts,
                leconSoulevee: _leconSoulevee,
                onCommencer: _commencerGlissement,
                onFinir: _finirGlissement,
                onDeposer: _deposer,
                motif: (code) => _motif(l, code),
              )),
            ],
          );
        },
      ),
    );
  }

  /// Les entités proposées au filtre, selon l'angle de lecture.
  List<(int, String)> _entites(ContenuEdt donnees) {
    final vues = <int, String>{};
    for (final lecon in donnees.lecons) {
      switch (_vue) {
        case Vue.division:
          vues[lecon.classeId] = lecon.classeNom;
        case Vue.enseignant:
          vues[lecon.professeurId] = lecon.professeurNom;
        case Vue.salle:
          vues[lecon.salleId] = lecon.salleNom;
      }
    }
    final liste = vues.entries.map((e) => (e.key, e.value)).toList();
    liste.sort((a, b) => a.$2.compareTo(b.$2));
    return liste;
  }
}

class _BarreFiltres extends StatelessWidget {
  const _BarreFiltres({
    required this.vue,
    required this.filtre,
    required this.entites,
    required this.onVue,
    required this.onFiltre,
  });

  final Vue vue;
  final int? filtre;
  final List<(int, String)> entites;
  final ValueChanged<Vue> onVue;
  final ValueChanged<int?> onFiltre;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return Padding(
      padding: const EdgeInsets.all(Jetons.m),
      child: Wrap(
        spacing: Jetons.m,
        runSpacing: Jetons.s,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          SegmentedButton<Vue>(
            segments: [
              ButtonSegment(
                  value: Vue.division,
                  icon: const Icon(Icons.school_outlined),
                  label: Text(l.parDivision)),
              ButtonSegment(
                  value: Vue.enseignant,
                  icon: const Icon(Icons.person_outline),
                  label: Text(l.parEnseignant)),
              ButtonSegment(
                  value: Vue.salle,
                  icon: const Icon(Icons.meeting_room_outlined),
                  label: Text(l.parSalle)),
            ],
            selected: {vue},
            onSelectionChanged: (choix) => onVue(choix.first),
            showSelectedIcon: false,
          ),
          SizedBox(
            width: 260,
            child: DropdownButtonFormField<int>(
              initialValue: filtre,
              isDense: true,
              decoration: const InputDecoration(isDense: true),
              items: [
                for (final entite in entites)
                  DropdownMenuItem(value: entite.$1, child: Text(entite.$2)),
              ],
              onChanged: onFiltre,
            ),
          ),
        ],
      ),
    );
  }
}

/// La grille elle-même : jours en colonnes, séances en lignes.
class _Plateau extends StatelessWidget {
  const _Plateau({
    required this.donnees,
    required this.vue,
    required this.filtre,
    required this.verdicts,
    required this.leconSoulevee,
    required this.onCommencer,
    required this.onFinir,
    required this.onDeposer,
    required this.motif,
  });

  final ContenuEdt donnees;
  final Vue vue;
  final int? filtre;
  final Map<(String, String), Verdict>? verdicts;
  final int? leconSoulevee;
  final void Function(Lecon) onCommencer;
  final VoidCallback onFinir;
  final Future<void> Function(Lecon, String, String) onDeposer;
  final String Function(String) motif;

  bool _concerne(Lecon lecon) => switch (vue) {
        Vue.division => lecon.classeId == filtre,
        Vue.enseignant => lecon.professeurId == filtre,
        Vue.salle => lecon.salleId == filtre,
      };

  @override
  Widget build(BuildContext contexte) {
    final grille = donnees.grille;
    // Sur téléphone, cinq colonnes de 60 px seraient illisibles : la
    // grille défile horizontalement en gardant des cases utilisables.
    const largeurHeure = 78.0;
    const largeurJour = 168.0;
    const hauteurLigne = 74.0;

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(
        width: largeurHeure + largeurJour * grille.jours.length,
        child: Column(
          children: [
            Row(
              children: [
                const SizedBox(width: largeurHeure),
                for (final jour in grille.jours)
                  SizedBox(
                    width: largeurJour,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: Jetons.s),
                      child: Text(jour,
                          textAlign: TextAlign.center,
                          style: Theme.of(contexte)
                              .textTheme
                              .titleSmall
                              ?.copyWith(fontWeight: FontWeight.w700)),
                    ),
                  ),
              ],
            ),
            const Divider(height: 1),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    for (var seance = 0;
                        seance < grille.horaires.length;
                        seance++)
                      SizedBox(
                        height: hauteurLigne,
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            SizedBox(
                              width: largeurHeure,
                              child: Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(grille.horaires[seance].$1,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.w600)),
                                    Text(grille.horaires[seance].$2,
                                        style: const TextStyle(
                                            fontSize: 11,
                                            color: Jetons.encreAttenuee)),
                                  ],
                                ),
                              ),
                            ),
                            for (var indexJour = 0;
                                indexJour < grille.jours.length;
                                indexJour++)
                              SizedBox(
                                width: largeurJour,
                                child: _Case(
                                  jour: grille.jours[indexJour],
                                  heure: grille.horaires[seance].$1,
                                  fermee: grille.estFermee(indexJour, seance),
                                  lecons: donnees
                                      .a(grille.jours[indexJour],
                                          grille.horaires[seance].$1)
                                      .where(_concerne)
                                      .toList(),
                                  verdict: verdicts?[(
                                    grille.jours[indexJour],
                                    grille.horaires[seance].$1
                                  )],
                                  enGlissement: leconSoulevee != null,
                                  vue: vue,
                                  onCommencer: onCommencer,
                                  onFinir: onFinir,
                                  onDeposer: onDeposer,
                                  motif: motif,
                                ),
                              ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Case extends StatelessWidget {
  const _Case({
    required this.jour,
    required this.heure,
    required this.fermee,
    required this.lecons,
    required this.verdict,
    required this.enGlissement,
    required this.vue,
    required this.onCommencer,
    required this.onFinir,
    required this.onDeposer,
    required this.motif,
  });

  final String jour;
  final String heure;
  final bool fermee;
  final List<Lecon> lecons;
  final Verdict? verdict;
  final bool enGlissement;
  final Vue vue;
  final void Function(Lecon) onCommencer;
  final VoidCallback onFinir;
  final Future<void> Function(Lecon, String, String) onDeposer;
  final String Function(String) motif;

  @override
  Widget build(BuildContext contexte) {
    // Pendant un glissement, la case dit d'elle-même si elle accepte.
    // L'état ne passe jamais par la seule couleur : une bordure pleine
    // ou pointillée, et une icône, le disent aussi.
    Color fond = Colors.transparent;
    Color bordure = Jetons.bordure;
    if (fermee) {
      fond = Jetons.attenue;
    } else if (enGlissement && verdict != null) {
      fond = verdict!.possible
          ? Jetons.succes.withValues(alpha: 0.10)
          : Jetons.danger.withValues(alpha: 0.06);
      bordure = verdict!.possible ? Jetons.succes : Jetons.danger;
    }

    final contenu = Container(
      margin: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: fond,
        border: Border.all(
          color: bordure,
          width: enGlissement && verdict != null ? 1.6 : 1,
        ),
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
      ),
      child: fermee
          ? const Center(
              child: Icon(Icons.block, size: 16, color: Jetons.encreAttenuee))
          : lecons.isEmpty
              ? (enGlissement && verdict != null
                  ? Center(
                      child: Icon(
                        verdict!.possible ? Icons.add : Icons.close,
                        size: 18,
                        color: verdict!.possible
                            ? Jetons.succes
                            : Jetons.danger,
                      ),
                    )
                  : null)
              : Column(
                  children: [
                    for (final lecon in lecons)
                      Expanded(
                        child: _Etiquette(
                          lecon: lecon,
                          vue: vue,
                          onCommencer: onCommencer,
                          onFinir: onFinir,
                        ),
                      ),
                  ],
                ),
    );

    if (fermee) return contenu;

    return DragTarget<Lecon>(
      onWillAcceptWithDetails: (details) =>
          verdict?.possible ?? true,
      onAcceptWithDetails: (details) =>
          onDeposer(details.data, jour, heure),
      builder: (contexte, _, __) {
        final aide = (enGlissement && verdict != null && !verdict!.possible)
            ? motif(verdict!.motif ?? '')
            : null;
        return aide == null
            ? contenu
            : Tooltip(message: aide, child: contenu);
      },
    );
  }
}

/// Une leçon dans sa case, saisissable.
class _Etiquette extends StatelessWidget {
  const _Etiquette({
    required this.lecon,
    required this.vue,
    required this.onCommencer,
    required this.onFinir,
  });

  final Lecon lecon;
  final Vue vue;
  final void Function(Lecon) onCommencer;
  final VoidCallback onFinir;

  /// La deuxième ligne dit ce que la vue courante ne montre pas déjà.
  String _detail() => switch (vue) {
        Vue.division => '${lecon.professeurNom} · ${lecon.salleNom}',
        Vue.enseignant => '${lecon.classeNom} · ${lecon.salleNom}',
        Vue.salle => '${lecon.classeNom} · ${lecon.professeurNom}',
      };

  @override
  Widget build(BuildContext contexte) {
    // La teinte vient de l'identifiant de la matière : deux matières
    // voisines ne se confondent pas, et la couleur reste la même d'une
    // semaine à l'autre.
    final teinte = Color.fromARGB(
      255,
      210 + (lecon.matiereId * 37) % 40,
      215 + (lecon.matiereId * 61) % 35,
      240 - (lecon.matiereId * 29) % 30,
    );

    final carte = Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
      decoration: BoxDecoration(
        color: teinte,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            lecon.matiereNom,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
                fontWeight: FontWeight.w700, fontSize: 12, height: 1.2),
          ),
          Text(
            _detail(),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
                fontSize: 10.5, color: Jetons.encreAttenuee, height: 1.2),
          ),
        ],
      ),
    );

    // Appui long plutôt que glissement immédiat : la grille défile
    // horizontalement sur téléphone, et un Draggable direct volerait
    // le geste de défilement. Le délai reste court pour qu'à la souris
    // le geste paraisse immédiat.
    return LongPressDraggable<Lecon>(
      data: lecon,
      delay: const Duration(milliseconds: 140),
      onDragStarted: () => onCommencer(lecon),
      onDragEnd: (_) => onFinir(),
      onDraggableCanceled: (_, __) => onFinir(),
      feedback: Material(
        color: Colors.transparent,
        child: Opacity(
          opacity: 0.92,
          child: SizedBox(width: 150, height: 46, child: carte),
        ),
      ),
      childWhenDragging: Opacity(opacity: 0.25, child: carte),
      child: carte,
    );
  }
}
