"""
Diagnostic pré-résolution.

Un modèle sur-contraint ressort du solveur avec un simple INFEASIBLE,
sans indiquer la cause — inexploitable pour le responsable qui saisit
les données. Ce module détecte en amont les incohérences structurelles
et les nomme précisément.

Deux niveaux :
  ERREUR        — rend la génération mathématiquement impossible
  AVERTISSEMENT — passe, mais produira un résultat de mauvaise qualité
"""

from collections import defaultdict
from typing import List, Optional, Sequence, Tuple

from .models import (
    Classe, CoursRequis, FenetrePedagogique, GrilleHoraire, Matiere, Options,
    Professeur, Salle,
)

ERREUR = "erreur"
AVERTISSEMENT = "avertissement"

Anomalie = Tuple[str, str]


def diagnostiquer(
    grille: GrilleHoraire,
    salles: Sequence[Salle],
    matieres: Sequence[Matiere],
    professeurs: Sequence[Professeur],
    classes: Sequence[Classe],
    cours_requis: Sequence[CoursRequis],
    options: Optional[Options] = None,
    fenetres_pedagogiques: Sequence[FenetrePedagogique] = (),
) -> List[Anomalie]:
    options = options or Options()
    idx_salles = {s.id: s for s in salles}
    idx_matieres = {m.id: m for m in matieres}
    idx_profs = {p.id: p for p in professeurs}
    idx_classes = {c.id: c for c in classes}

    anomalies: List[Anomalie] = []
    err = lambda m: anomalies.append((ERREUR, m))
    avert = lambda m: anomalies.append((AVERTISSEMENT, m))

    nb_creneaux = len(grille.creneaux)
    nb_jours = len(grille.jours)
    par_jour = grille.par_jour()

    interdits = defaultdict(set)
    for fenetre in fenetres_pedagogiques:
        for creneau in grille.creneaux:
            if (creneau.index_jour == fenetre.index_jour
                    and creneau.index_seance in fenetre.seances_bloquees):
                interdits[fenetre.matiere_id].add(creneau.id)

    # ── 1. Références et cohérence de chaque cours requis ─────────
    cours_valides: List[CoursRequis] = []
    for cr in cours_requis:
        if cr.classe_id not in idx_classes:
            err(f"Cours #{cr.id} : classe {cr.classe_id} inconnue.")
            continue
        if cr.matiere_id not in idx_matieres:
            err(f"Cours #{cr.id} : matière {cr.matiere_id} inconnue.")
            continue
        if cr.professeur_id not in idx_profs:
            err(f"Cours #{cr.id} : professeur {cr.professeur_id} inconnu.")
            continue

        classe, matiere, prof = (idx_classes[cr.classe_id],
                                 idx_matieres[cr.matiere_id],
                                 idx_profs[cr.professeur_id])

        if cr.heures_par_semaine <= 0:
            err(f"{classe.nom} / {matiere.nom} : volume horaire nul ou négatif.")
            continue

        if (options.verifier_competence_professeur and prof.matieres_ids
                and cr.matiere_id not in prof.matieres_ids):
            err(f"{prof.nom_complet} n'enseigne pas « {matiere.nom} » "
                f"(affecté à {classe.nom}). Corrigez l'affectation ou "
                f"ajoutez la matière au professeur.")
            continue

        if cr.nb_seances_doubles * 2 > cr.heures_par_semaine:
            err(f"{classe.nom} / {matiere.nom} : {cr.nb_seances_doubles} séances "
                f"doubles demandées ({cr.nb_seances_doubles * 2} h) pour un volume "
                f"de {cr.heures_par_semaine} h seulement.")
            continue

        plafond_hebdo = cr.max_heures_par_jour * nb_jours
        if cr.heures_par_semaine > plafond_hebdo:
            err(f"{classe.nom} / {matiere.nom} : {cr.heures_par_semaine} h/semaine "
                f"impossibles avec un plafond de {cr.max_heures_par_jour} h/jour "
                f"sur {nb_jours} jours (max {plafond_hebdo} h).")
            continue

        # Une salle compatible existe-t-elle ?
        type_requis = cr.type_salle_requis or matiere.type_salle_requis
        if type_requis == options.type_salle_ordinaire:
            type_requis = None
        effectif = cr.effectif or classe.effectif
        if cr.couplage_id:
            effectif = (effectif + 1) // 2      # demi-groupe
        if type_requis:
            compat = [s for s in salles if s.type == type_requis]
            if not compat:
                err(f"{classe.nom} / {matiere.nom} exige une salle de type "
                    f"« {type_requis} » : aucune n'est déclarée.")
                continue
            if options.verifier_capacite_salle and not any(
                    s.capacite >= effectif for s in compat):
                err(f"{classe.nom} / {matiere.nom} : aucune salle « {type_requis} » "
                    f"ne peut accueillir {effectif} élèves "
                    f"(plus grande : {max(s.capacite for s in compat)} places).")
                continue
        elif not (options.salle_attitree and classe.salle_attitree_id):
            compat = [s for s in salles
                      if not options.reserver_salles_specialisees
                      or s.type == options.type_salle_ordinaire]
            if not compat:
                err(f"{classe.nom} / {matiere.nom} : aucune salle ordinaire disponible.")
                continue
            if options.verifier_capacite_salle and not any(
                    s.capacite >= effectif for s in compat):
                err(f"{classe.nom} / {matiere.nom} : aucune salle ordinaire ne peut "
                    f"accueillir {effectif} élèves.")
                continue

        # Fenêtres pédagogiques : reste-t-il assez de créneaux ?
        bloques = interdits.get(cr.matiere_id, set()) | cr.creneaux_interdits
        ouverts = {c.id for c in grille.creneaux} - bloques
        if prof.creneaux_disponibles:
            ouverts &= prof.creneaux_disponibles
        if len(ouverts) < cr.heures_par_semaine:
            err(f"{classe.nom} / {matiere.nom} : {cr.heures_par_semaine} h à placer "
                f"pour {len(ouverts)} créneaux restants une fois retirées les "
                f"fenêtres pédagogiques et les indisponibilités de "
                f"{prof.nom_complet}.")
            continue

        cours_valides.append(cr)

    # ── 2. Salles attitrées ───────────────────────────────────────
    salles_attitrees = defaultdict(list)
    for classe in classes:
        if not classe.salle_attitree_id:
            if options.salle_attitree:
                avert(f"{classe.nom} n'a pas de salle attitrée : les élèves "
                      f"changeront de salle à chaque heure.")
            continue
        if classe.salle_attitree_id not in idx_salles:
            err(f"{classe.nom} : salle attitrée {classe.salle_attitree_id} inconnue.")
            continue
        salle = idx_salles[classe.salle_attitree_id]
        salles_attitrees[salle.id].append(classe.nom)
        if salle.capacite < classe.effectif:
            avert(f"{classe.nom} ({classe.effectif} élèves) est attitrée à "
                  f"{salle.nom} qui n'a que {salle.capacite} places.")
    for salle_id, noms in salles_attitrees.items():
        if len(noms) > 1:
            err(f"{idx_salles[salle_id].nom} est attitrée à plusieurs classes : "
                f"{', '.join(noms)}.")

    # ── 3. Charge des classes ─────────────────────────────────────
    charge_classe = defaultdict(int)
    couplages_comptes = set()
    for cr in cours_valides:
        if cr.couplage_id:
            cle = (cr.classe_id, cr.couplage_id)
            if cle in couplages_comptes:
                continue          # l'autre demi-groupe est simultané
            couplages_comptes.add(cle)
        charge_classe[cr.classe_id] += cr.heures_par_semaine
    for classe in classes:
        charge = charge_classe.get(classe.id, 0)
        if charge == 0:
            avert(f"{classe.nom} n'a aucun cours à planifier.")
            continue
        if charge > nb_creneaux:
            err(f"{classe.nom} : {charge} h/semaine à placer pour seulement "
                f"{nb_creneaux} créneaux dans la grille horaire.")
        plafond = classe.max_heures_par_jour * nb_jours
        if charge > plafond:
            err(f"{classe.nom} : {charge} h/semaine impossibles avec un plafond "
                f"de {classe.max_heures_par_jour} h/jour sur {nb_jours} jours "
                f"(max {plafond} h).")
        marge = nb_creneaux - charge
        if 0 <= marge <= 2:
            avert(f"{classe.nom} : {charge} h pour {nb_creneaux} créneaux ouverts "
                  f"(marge de {marge} h). L'emploi du temps est quasi saturé — "
                  f"les souhaits de sortie anticipée ne pourront pas être honorés.")
        if classe.max_demi_journees is not None:
            capacite_dj = 0
            for creneaux_dj in sorted(
                    (len(v) for v in grille.par_demi_journee().values()), reverse=True
            )[:classe.max_demi_journees]:
                capacite_dj += creneaux_dj
            if charge > capacite_dj:
                err(f"{classe.nom} : {charge} h/semaine ne tiennent pas en "
                    f"{classe.max_demi_journees} demi-journées ({capacite_dj} h).")

    # ── 4. Charge des professeurs ─────────────────────────────────
    charge_prof = defaultdict(int)
    for cr in cours_valides:
        charge_prof[cr.professeur_id] += cr.heures_par_semaine
    for prof in professeurs:
        charge = charge_prof.get(prof.id, 0)
        if charge == 0:
            continue
        dispo = (len(prof.creneaux_disponibles) if prof.creneaux_disponibles
                 else nb_creneaux)
        if charge > dispo:
            err(f"{prof.nom_complet} : {charge} h/semaine à assurer pour "
                f"seulement {dispo} créneaux de disponibilité.")
        plafond_jour = prof.max_heures_par_jour * nb_jours
        if charge > plafond_jour:
            err(f"{prof.nom_complet} : {charge} h/semaine dépassent le plafond de "
                f"{prof.max_heures_par_jour} h/jour sur {nb_jours} jours.")
        if prof.max_jours_presence is not None:
            capacite = 0
            for creneaux_j in sorted((len(v) for v in par_jour.values()),
                                     reverse=True)[:prof.max_jours_presence]:
                capacite += min(creneaux_j, prof.max_heures_par_jour)
            if charge > capacite:
                err(f"{prof.nom_complet} : {charge} h/semaine ne tiennent pas en "
                    f"{prof.max_jours_presence} jours de présence ({capacite} h max).")
        if charge > dispo * 0.85:
            avert(f"{prof.nom_complet} est chargé à "
                  f"{charge}/{dispo} créneaux : peu de marge de manœuvre.")

    # ── 5. Capacité des salles par type ───────────────────────────
    besoin_type = defaultdict(int)
    for cr in cours_valides:
        type_requis = cr.type_salle_requis or idx_matieres[cr.matiere_id].type_salle_requis
        if type_requis and type_requis != options.type_salle_ordinaire:
            besoin_type[type_requis] += cr.heures_par_semaine
        elif (not (options.salle_attitree and idx_classes[cr.classe_id].salle_attitree_id)
              or cr.couplage_id):
            # Salle ordinaire : classe sans salle attitrée, ou second
            # demi-groupe d'un fouj qu'il faut accueillir ailleurs.
            besoin_type[options.type_salle_ordinaire] += cr.heures_par_semaine
    for type_salle, besoin in besoin_type.items():
        offre = sum(1 for s in salles if s.type == type_salle) * nb_creneaux
        if besoin > offre:
            err(f"Salles « {type_salle} » : {besoin} h à placer pour une capacité "
                f"totale de {offre} h "
                f"({sum(1 for s in salles if s.type == type_salle)} salle(s) × "
                f"{nb_creneaux} créneaux).")
        elif besoin > offre * 0.9:
            avert(f"Salles « {type_salle} » occupées à "
                  f"{100 * besoin // max(offre, 1)} % : très peu de marge.")

    # ── 6. Doublons ───────────────────────────────────────────────
    vus = defaultdict(list)
    for cr in cours_valides:
        if cr.couplage_id:
            continue          # TD/TP de fouj : ce n'est pas un doublon du cours
        vus[(cr.classe_id, cr.matiere_id)].append(cr)
    for (classe_id, matiere_id), liste in vus.items():
        if len(liste) > 1:
            avert(f"{idx_classes[classe_id].nom} / {idx_matieres[matiere_id].nom} : "
                  f"{len(liste)} lignes de cours distinctes "
                  f"(professeurs différents ?). Vérifiez qu'il ne s'agit pas d'un doublon.")

    return anomalies


def formater(anomalies: Sequence[Anomalie]) -> str:
    """Rend les anomalies lisibles dans un terminal ou un message d'API."""
    if not anomalies:
        return "Aucune anomalie détectée."
    lignes = []
    for niveau, message in anomalies:
        puce = "✗" if niveau == ERREUR else "!"
        lignes.append(f"  {puce} {message}")
    return "\n".join(lignes)


def erreurs(anomalies: Sequence[Anomalie]) -> List[str]:
    return [m for n, m in anomalies if n == ERREUR]
