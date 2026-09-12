import 'package:flutter/material.dart';

import '../core/ressources.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';
import '../widgets/formulaire.dart';
import '../widgets/liste_ressource.dart';

/// Les types de salle proposés. Une liste fermée évite qu'un « labo »
/// et un « laboratoire » saisis au fil de l'eau ne se retrouvent jamais.
const _typesSalle = ['classique', 'labo', 'labo_bio', 'labo_physique',
    'info', 'sport', 'atelier'];
const _niveaux = ['primaire', 'moyen', 'secondaire'];

String _texte(Object? valeur) => valeur == null ? '' : '$valeur';

class PageEnseignants extends StatelessWidget {
  const PageEnseignants({super.key});

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return ListeRessource(
      dependances: const [(cle: 'matieres', ressource: ressourceMatieres)],
      definition: Definition(
        ressource: ressourceEnseignants,
        titre: l.enseignants,
        icone: Icons.people_outline,
        aideVide: l.aideEnseignantsVide,
        libelle: (e) => '${_texte(e['prenom'])} ${_texte(e['nom'])}'.trim(),
        sousTitre: (contexte, e) {
          final morceaux = <String>[
            if (e['max_heures_par_semaine'] != null)
              contexte.l10n.heuresParSemaine(e['max_heures_par_semaine'] as int),
            contexte.l10n.heuresParJour(e['max_heures_par_jour'] as int),
            if (e['email'] != null) '${e['email']}',
          ];
          return morceaux.join(' · ');
        },
        champs: (contexte, dependances) {
          final l = contexte.l10n;
          return [
            Champ(cle: 'prenom', libelle: l.prenom, obligatoire: true),
            Champ(cle: 'nom', libelle: l.nom, obligatoire: true),
            Champ(cle: 'email', libelle: l.email),
            Champ(cle: 'telephone', libelle: l.telephone),
            Champ(
              cle: 'matieres_ids',
              libelle: l.matieres,
              type: TypeChamp.multiChoix,
              aide: l.aideMatieresEnseignant,
              options: [
                for (final matiere in dependances['matieres'] ?? const [])
                  (valeur: matiere['id'] as Object, libelle: '${matiere['nom']}'),
              ],
            ),
            Champ(
              cle: 'max_heures_consecutives',
              libelle: l.heuresConsecutivesMax,
              type: TypeChamp.entier,
              defaut: 4,
              minimum: 1,
              maximum: 12,
            ),
            Champ(
              cle: 'max_heures_par_jour',
              libelle: l.heuresParJourMax,
              type: TypeChamp.entier,
              defaut: 6,
              minimum: 1,
              maximum: 12,
            ),
            Champ(
              cle: 'max_heures_par_semaine',
              libelle: l.heuresParSemaineMax,
              type: TypeChamp.entier,
              aide: l.aidePlafondHebdo,
              minimum: 1,
              maximum: 60,
            ),
            Champ(
              cle: 'assure_permanences',
              libelle: l.assurePermanences,
              type: TypeChamp.booleen,
              aide: l.aidePermanences,
              defaut: true,
            ),
          ];
        },
      ),
    );
  }
}

class PageMatieres extends StatelessWidget {
  const PageMatieres({super.key});

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return ListeRessource(
      definition: Definition(
        ressource: ressourceMatieres,
        titre: l.matieres,
        icone: Icons.menu_book_outlined,
        aideVide: l.aideMatieresVide,
        libelle: (e) => _texte(e['nom']),
        sousTitre: (contexte, e) => [
          contexte.l10n.coefficientValeur('${e['coefficient']}'),
          if (e['type_salle_requis'] != null) '${e['type_salle_requis']}',
        ].join(' · '),
        champs: (contexte, _) {
          final l = contexte.l10n;
          return [
            Champ(cle: 'nom', libelle: l.nom, obligatoire: true),
            Champ(
              cle: 'coefficient',
              libelle: l.coefficient,
              type: TypeChamp.decimal,
              defaut: 1,
              minimum: 0,
              maximum: 20,
            ),
            Champ(
              cle: 'type_salle_requis',
              libelle: l.typeSalleRequis,
              type: TypeChamp.choix,
              aide: l.aideTypeSalle,
              options: [
                for (final type in _typesSalle)
                  (valeur: type as Object, libelle: type),
              ],
            ),
          ];
        },
      ),
    );
  }
}

class PageSalles extends StatelessWidget {
  const PageSalles({super.key});

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return ListeRessource(
      definition: Definition(
        ressource: ressourceSalles,
        titre: l.salles,
        icone: Icons.meeting_room_outlined,
        aideVide: l.aideSallesVide,
        libelle: (e) => _texte(e['nom']),
        sousTitre: (contexte, e) =>
            '${e['type']} · ${contexte.l10n.places(e['capacite'] as int)}',
        champs: (contexte, _) {
          final l = contexte.l10n;
          return [
            Champ(cle: 'nom', libelle: l.nom, obligatoire: true),
            Champ(
              cle: 'capacite',
              libelle: l.capacite,
              type: TypeChamp.entier,
              defaut: 30,
              minimum: 1,
              maximum: 500,
            ),
            Champ(
              cle: 'type',
              libelle: l.typeSalle,
              type: TypeChamp.choix,
              obligatoire: true,
              defaut: 'classique',
              options: [
                for (final type in _typesSalle)
                  (valeur: type as Object, libelle: type),
              ],
            ),
          ];
        },
      ),
    );
  }
}

class PageDivisions extends StatelessWidget {
  const PageDivisions({super.key});

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return ListeRessource(
      dependances: const [(cle: 'salles', ressource: ressourceSalles)],
      definition: Definition(
        ressource: ressourceDivisions,
        titre: l.divisions,
        icone: Icons.school_outlined,
        aideVide: l.aideDivisionsVide,
        libelle: (e) => _texte(e['nom']),
        sousTitre: (contexte, e) => [
          '${e['niveau']}',
          contexte.l10n.eleves(e['effectif'] as int),
          contexte.l10n.heuresParJour(e['max_heures_par_jour'] as int),
        ].join(' · '),
        champs: (contexte, dependances) {
          final l = contexte.l10n;
          return [
            Champ(cle: 'nom', libelle: l.nom, obligatoire: true),
            Champ(
              cle: 'niveau',
              libelle: l.niveau,
              type: TypeChamp.choix,
              obligatoire: true,
              defaut: 'moyen',
              options: [
                for (final niveau in _niveaux)
                  (valeur: niveau as Object, libelle: niveau),
              ],
            ),
            Champ(
              cle: 'effectif',
              libelle: l.effectif,
              type: TypeChamp.entier,
              defaut: 30,
              minimum: 1,
              maximum: 100,
            ),
            Champ(
              cle: 'salle_attitree_id',
              libelle: l.salleAttitree,
              type: TypeChamp.choix,
              aide: l.aideSalleAttitree,
              options: [
                for (final salle in dependances['salles'] ?? const [])
                  (valeur: salle['id'] as Object, libelle: '${salle['nom']}'),
              ],
            ),
            Champ(
              cle: 'max_heures_par_jour',
              libelle: l.heuresParJourMax,
              type: TypeChamp.entier,
              defaut: 6,
              minimum: 1,
              maximum: 12,
            ),
          ];
        },
      ),
    );
  }
}

class PageProgramme extends StatelessWidget {
  const PageProgramme({super.key});

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return ListeRessource(
      dependances: const [
        (cle: 'divisions', ressource: ressourceDivisions),
        (cle: 'matieres', ressource: ressourceMatieres),
        (cle: 'enseignants', ressource: ressourceEnseignants),
      ],
      definition: Definition(
        ressource: ressourceProgramme,
        titre: l.programme,
        icone: Icons.list_alt_outlined,
        aideVide: l.aideProgrammeVide,
        libelle: (e) =>
            '${_texte(e['classe_nom'])} · ${_texte(e['matiere_nom'])}',
        sousTitre: (contexte, e) {
          final l = contexte.l10n;
          return [
            _texte(e['professeur_nom']),
            l.heuresParSemaine(e['heures_par_semaine'] as int),
            if ((e['nb_seances_doubles'] as int? ?? 0) > 0)
              l.blocsDeDeuxHeures(e['nb_seances_doubles'] as int),
            if (e['couplage_id'] != null)
              'fouj ${_texte(e['groupe'])}',
          ].where((m) => m.isNotEmpty).join(' · ');
        },
        champs: (contexte, dependances) {
          final l = contexte.l10n;
          return [
            Champ(
              cle: 'classe_id',
              libelle: l.division,
              type: TypeChamp.choix,
              obligatoire: true,
              options: [
                for (final division in dependances['divisions'] ?? const [])
                  (valeur: division['id'] as Object,
                      libelle: '${division['nom']}'),
              ],
            ),
            Champ(
              cle: 'matiere_id',
              libelle: l.matiere,
              type: TypeChamp.choix,
              obligatoire: true,
              options: [
                for (final matiere in dependances['matieres'] ?? const [])
                  (valeur: matiere['id'] as Object, libelle: '${matiere['nom']}'),
              ],
            ),
            Champ(
              cle: 'professeur_id',
              libelle: l.enseignant,
              type: TypeChamp.choix,
              obligatoire: true,
              options: [
                for (final enseignant
                    in dependances['enseignants'] ?? const [])
                  (
                    valeur: enseignant['id'] as Object,
                    libelle:
                        '${enseignant['prenom']} ${enseignant['nom']}'.trim()
                  ),
              ],
            ),
            Champ(
              cle: 'heures_par_semaine',
              libelle: l.heuresParSemaineLibelle,
              type: TypeChamp.entier,
              obligatoire: true,
              defaut: 1,
              minimum: 1,
              maximum: 40,
            ),
            Champ(
              cle: 'nb_seances_doubles',
              libelle: l.blocsDeuxHeures,
              type: TypeChamp.entier,
              aide: l.aideBlocs,
              defaut: 0,
              minimum: 0,
              maximum: 10,
            ),
            Champ(
              cle: 'max_heures_par_jour',
              libelle: l.maxParJour,
              type: TypeChamp.entier,
              defaut: 2,
              minimum: 1,
              maximum: 12,
            ),
            Champ(
              cle: 'couplage_id',
              libelle: l.fouj,
              aide: l.aideFouj,
            ),
            Champ(
              cle: 'groupe',
              libelle: l.demiGroupe,
              type: TypeChamp.choix,
              options: const [
                (valeur: 'G1', libelle: 'G1'),
                (valeur: 'G2', libelle: 'G2'),
              ],
            ),
          ];
        },
      ),
    );
  }
}

/// Utilisé par le tableau de bord pour l'espacement homogène.
const paddingEcran = EdgeInsets.all(Jetons.l);
