import 'package:flutter/material.dart';

import '../l10n/traductions.dart';

/// Une entrée de la navigation principale.
@immutable
class Destination {
  const Destination({
    required this.chemin,
    required this.icone,
    required this.iconeActive,
    required this.libelle,
    this.principale = false,
  });

  final String chemin;
  final IconData icone;
  final IconData iconeActive;

  /// Le libellé se lit dans les traductions au moment de l'affichage :
  /// stocker le texte ici le figerait dans la langue de démarrage.
  final String Function(L) libelle;

  /// Les destinations principales tiennent dans la barre du bas ; les
  /// autres passent par « Plus », sous peine de dépasser les cinq
  /// entrées au-delà desquelles une barre devient illisible.
  final bool principale;
}

const destinations = <Destination>[
  Destination(
    chemin: '/tableau-de-bord',
    icone: Icons.dashboard_outlined,
    iconeActive: Icons.dashboard,
    libelle: _tableauDeBord,
    principale: true,
  ),
  Destination(
    chemin: '/emplois-du-temps',
    icone: Icons.calendar_month_outlined,
    iconeActive: Icons.calendar_month,
    libelle: _emplois,
    principale: true,
  ),
  Destination(
    chemin: '/programme',
    icone: Icons.list_alt_outlined,
    iconeActive: Icons.list_alt,
    libelle: _programme,
    principale: true,
  ),
  Destination(
    chemin: '/donnees',
    icone: Icons.table_chart_outlined,
    iconeActive: Icons.table_chart,
    libelle: _donnees,
    principale: true,
  ),
  Destination(
    chemin: '/enseignants',
    icone: Icons.people_outline,
    iconeActive: Icons.people,
    libelle: _enseignants,
  ),
  Destination(
    chemin: '/matieres',
    icone: Icons.menu_book_outlined,
    iconeActive: Icons.menu_book,
    libelle: _matieres,
  ),
  Destination(
    chemin: '/divisions',
    icone: Icons.school_outlined,
    iconeActive: Icons.school,
    libelle: _divisions,
  ),
  Destination(
    chemin: '/salles',
    icone: Icons.meeting_room_outlined,
    iconeActive: Icons.meeting_room,
    libelle: _salles,
  ),
  Destination(
    chemin: '/reglages',
    icone: Icons.tune_outlined,
    iconeActive: Icons.tune,
    libelle: _reglages,
  ),
];

String _tableauDeBord(L l) => l.tableauDeBord;
String _emplois(L l) => l.emploisDuTemps;
String _programme(L l) => l.programme;
String _donnees(L l) => l.donnees;
String _enseignants(L l) => l.enseignants;
String _matieres(L l) => l.matieres;
String _divisions(L l) => l.divisions;
String _salles(L l) => l.salles;
String _reglages(L l) => l.reglages;
