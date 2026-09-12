import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api.dart';
import 'session.dart';

/// Une leçon posée sur la grille.
@immutable
class Lecon {
  const Lecon({
    required this.id,
    required this.classeId,
    required this.matiereId,
    required this.professeurId,
    required this.salleId,
    required this.jour,
    required this.heureDebut,
    required this.classeNom,
    required this.matiereNom,
    required this.professeurNom,
    required this.salleNom,
  });

  factory Lecon.depuisJson(Map<String, dynamic> json) => Lecon(
        id: json['id'] as int,
        classeId: json['classe_id'] as int,
        matiereId: json['matiere_id'] as int,
        professeurId: json['professeur_id'] as int,
        salleId: json['salle_id'] as int,
        jour: '${json['jour']}',
        heureDebut: '${json['heure_debut']}',
        classeNom: '${json['classe_nom'] ?? ''}',
        matiereNom: '${json['matiere_nom'] ?? ''}',
        professeurNom: '${json['professeur_nom'] ?? ''}',
        salleNom: '${json['salle_nom'] ?? ''}',
      );

  final int id;
  final int classeId;
  final int matiereId;
  final int professeurId;
  final int salleId;
  final String jour;
  final String heureDebut;
  final String classeNom;
  final String matiereNom;
  final String professeurNom;
  final String salleNom;
}

/// Grille horaire de l'établissement.
@immutable
class Grille {
  const Grille({
    required this.jours,
    required this.horaires,
    required this.fermetures,
  });

  factory Grille.depuisJson(Map<String, dynamic> json) => Grille(
        jours: (json['jours'] as List).map((j) => '$j').toList(),
        horaires: (json['horaires'] as List)
            .map((h) => ('${(h as List)[0]}', '${h[1]}'))
            .toList(),
        fermetures: {
          for (final fermeture in (json['fermetures'] as List? ?? const []))
            for (final seance in ((fermeture as List)[1] as List))
              (fermeture[0] as int, seance as int),
        },
      );

  final List<String> jours;
  final List<(String, String)> horaires;
  final Set<(int, int)> fermetures;

  bool estFermee(int indexJour, int seance) =>
      fermetures.contains((indexJour, seance));
}

/// Ce que l'écran d'emploi du temps a besoin de connaître.
@immutable
class ContenuEdt {
  const ContenuEdt({required this.grille, required this.lecons});

  final Grille grille;
  final List<Lecon> lecons;

  /// Leçons d'une case, un fouj en comptant deux.
  List<Lecon> a(String jour, String heure) => lecons
      .where((l) => l.jour == jour && l.heureDebut == heure)
      .toList(growable: false);
}

final edtProvider = FutureProvider.autoDispose
    .family<ContenuEdt, int>((ref, edtId) async {
  final api = ref.watch(apiProvider);
  final reponses = await Future.wait([
    api.get('/parametres'),
    api.get('/emplois-du-temps/$edtId/lecons'),
  ]);
  return ContenuEdt(
    grille: Grille.depuisJson(
        (reponses[0] as Map<String, dynamic>)['grille'] as Map<String, dynamic>),
    lecons: (reponses[1] as List)
        .map((j) => Lecon.depuisJson(j as Map<String, dynamic>))
        .toList(),
  );
});

final listeEdtProvider = FutureProvider.autoDispose((ref) async {
  final reponse = await ref.watch(apiProvider).get('/emplois-du-temps/') as List;
  return reponse.cast<Map<String, dynamic>>();
});

/// Verdict du serveur sur un créneau, pour une leçon en cours de
/// déplacement.
@immutable
class Verdict {
  const Verdict({required this.possible, this.motif});

  final bool possible;
  final String? motif;
}

/// Interroge le serveur sur les créneaux ouverts à une leçon.
Future<Map<(String, String), Verdict>> creneauxPossibles(
    Api api, int edtId, int leconId) async {
  final reponse = await api
      .get('/emplois-du-temps/$edtId/lecons/$leconId/creneaux') as Map;
  return {
    for (final creneau in (reponse['creneaux'] as List))
      ('${creneau['jour']}', '${creneau['heure_debut']}'): Verdict(
        possible: creneau['possible'] == true,
        motif: creneau['motif'] as String?,
      ),
  };
}

Future<void> deplacerLecon(
    Api api, int edtId, int leconId, String jour, String heure) {
  return api.patch('/emplois-du-temps/$edtId/lecons/$leconId',
      corps: {'jour': jour, 'heure_debut': heure});
}
