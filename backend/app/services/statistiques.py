"""
Statistiques d'un emploi du temps enregistré.

Les indicateurs de la génération décrivent la solution au moment où le
solveur la rend. Un emploi du temps se relit des mois plus tard, se
retouche à la main, et se compare à celui de l'an dernier : ces
statistiques se recalculent donc à partir des leçons en base et de la
grille horaire, sans dépendre de la tâche qui les a produites.

Deux conventions, les mêmes que pour le solveur :

  • pendant un fouj, deux leçons occupent le même créneau pour deux
    demi-groupes — la division n'y passe qu'une heure ;
  • un trou est une heure creuse ENTRE deux cours de la même
    demi-journée : la pause déjeuner n'est pas du temps perdu.
"""

from collections import Counter, defaultdict
from typing import Dict, List

from sqlalchemy.orm import Session

from ..models.schedule import EmploiDuTemps
from . import parametres


def _positions(occupees: set, ouvertes: List[int]) -> List[int]:
    """Rangs occupés dans la liste des séances ouvertes d'une plage."""
    return sorted(i for i, seance in enumerate(ouvertes) if seance in occupees)


def _trous(positions: List[int]) -> int:
    """Heures creuses entre le premier et le dernier cours."""
    if len(positions) < 2:
        return 0
    return positions[-1] - positions[0] + 1 - len(positions)


def calculer(db: Session, ecole_id: int, edt: EmploiDuTemps) -> Dict:
    reglages = parametres.lire(db, ecole_id)
    grille = reglages.grille
    horaires = [tuple(h) for h in grille.horaires]
    debuts = [h[0] for h in horaires]
    index_seance = {debut: i for i, debut in enumerate(debuts)}
    index_jour = {nom: i for i, nom in enumerate(grille.jours)}

    fermees = {(j, s) for j, seances in grille.fermetures for s in seances}
    # Séances ouvertes de chaque journée, et de chaque demi-journée.
    ouvertes_jour = {
        nom: [s for s in range(len(horaires)) if (j, s) not in fermees]
        for j, nom in enumerate(grille.jours)
    }
    ouvertes_demi = {
        (nom, shift): [s for s in seances if (j, s) not in fermees]
        for j, nom in enumerate(grille.jours)
        for shift, seances in grille.shifts
    }
    demi_de_seance = {s: shift for shift, seances in grille.shifts
                      for s in seances}

    # ── Dépouillement des leçons ─────────────────────────────────
    prof_jour = defaultdict(set)        # (prof, jour) → séances
    classe_jour = defaultdict(set)      # (classe, jour) → séances (fouj dédoublonné)
    # (classe, jour) → {matière: séances} : une matière vue deux fois
    # dans la journée occupe deux créneaux distincts.
    matiere_jour = defaultdict(lambda: defaultdict(set))
    noms_profs, noms_classes = {}, {}
    hors_grille = 0

    for l in edt.lecons:
        seance = index_seance.get(l.heure_debut)
        if seance is None or l.jour not in index_jour:
            hors_grille += 1        # la grille a changé depuis la génération
            continue
        prof_jour[(l.professeur_id, l.jour)].add(seance)
        classe_jour[(l.classe_id, l.jour)].add(seance)
        matiere_jour[(l.classe_id, l.jour)][l.matiere_id].add(seance)
        if l.professeur and l.professeur_id not in noms_profs:
            noms_profs[l.professeur_id] = l.professeur.nom_complet
        if l.classe and l.classe_id not in noms_classes:
            noms_classes[l.classe_id] = l.classe.nom

    # ── Professeurs ──────────────────────────────────────────────
    heures_prof = defaultdict(int)
    for (prof_id, _jour), seances in prof_jour.items():
        heures_prof[prof_id] += len(seances)

    professeurs = []
    for prof_id, heures in heures_prof.items():
        jours = [j for (p, j) in prof_jour if p == prof_id]
        trous = isolees = creuses = 0
        charges = Counter()
        for jour in jours:
            occupees = prof_jour[(prof_id, jour)]
            charges[len(occupees)] += 1
            creuses += _trous(_positions(occupees, ouvertes_jour[jour]))
            for shift, _ in grille.shifts:
                dans = {s for s in occupees if demi_de_seance.get(s) == shift}
                if not dans:
                    continue
                trous += _trous(_positions(dans, ouvertes_demi[(jour, shift)]))
                if len(dans) == 1:
                    isolees += 1
        professeurs.append({
            "id": prof_id,
            "nom": noms_profs.get(prof_id, f"#{prof_id}"),
            "heures": heures,
            "jours_presence": len(jours),
            "trous": trous,
            "heures_creuses_journee": creuses,
            "demi_journees_isolees": isolees,
            "charge_max": max(charges) if charges else 0,
            "charges": dict(sorted(charges.items())),
        })
    professeurs.sort(key=lambda p: (-p["heures"], p["nom"]))

    # ── Divisions ────────────────────────────────────────────────
    derniere_ouverte = {jour: (seances[-1] if seances else None)
                        for jour, seances in ouvertes_jour.items()}
    classes = []
    for classe_id in sorted(noms_classes, key=lambda c: noms_classes[c]):
        jours = [j for (c, j) in classe_jour if c == classe_id]
        heures = sum(len(classe_jour[(classe_id, j)]) for j in jours)
        trous = tardives = 0
        charges = []
        doublees_max = trois_heures = 0
        for jour in jours:
            occupees = classe_jour[(classe_id, jour)]
            charges.append(len(occupees))
            trous += _trous(_positions(occupees, ouvertes_jour[jour]))
            if derniere_ouverte[jour] in occupees:
                tardives += 1
            du_jour = matiere_jour[(classe_id, jour)]
            doublees = sum(1 for ss in du_jour.values() if len(ss) >= 2)
            trois_heures += sum(1 for ss in du_jour.values() if len(ss) >= 3)
            doublees_max = max(doublees_max, doublees)
        classes.append({
            "id": classe_id,
            "nom": noms_classes[classe_id],
            "heures": heures,
            "trous": trous,
            "charge_min": min(charges) if charges else 0,
            "charge_max": max(charges) if charges else 0,
            "journees_finissant_tard": tardives,
            "matieres_doublees_max": doublees_max,
            "matieres_a_trois_heures": trois_heures,
        })

    # ── Occupation par séance ────────────────────────────────────
    nb_classes = len(noms_classes) or 1
    occupation = []
    for seance, (debut, fin) in enumerate(horaires):
        occupe = possible = 0
        for j, jour in enumerate(grille.jours):
            if (j, seance) in fermees:
                continue
            possible += nb_classes
            occupe += sum(1 for (c, jr), ss in classe_jour.items()
                          if jr == jour and seance in ss)
        occupation.append({
            "debut": debut, "fin": fin,
            "occupe": occupe, "possible": possible,
        })

    charges_profs = Counter()
    for stats in professeurs:
        for volume, nombre in stats["charges"].items():
            charges_profs[volume] += nombre

    return {
        "emploi_du_temps_id": edt.id,
        "nom": edt.nom,
        "grille": {"jours": list(grille.jours),
                   "horaires": [list(h) for h in horaires]},
        "totaux": {
            "lecons": len(edt.lecons),
            "professeurs": len(professeurs),
            "classes": len(classes),
            "heures_classes": sum(c["heures"] for c in classes),
            "lecons_hors_grille": hors_grille,
        },
        "resume": {
            "trous_professeurs": sum(p["trous"] for p in professeurs),
            "trous_classes": sum(c["trous"] for c in classes),
            "demi_journees_isolees": sum(p["demi_journees_isolees"]
                                         for p in professeurs),
            "charges_quotidiennes": dict(sorted(charges_profs.items())),
            "matieres_a_trois_heures": sum(c["matieres_a_trois_heures"]
                                           for c in classes),
            "heures_par_professeur_min": min((p["heures"] for p in professeurs),
                                             default=0),
            "heures_par_professeur_max": max((p["heures"] for p in professeurs),
                                             default=0),
        },
        "professeurs": professeurs,
        "classes": classes,
        "occupation_seances": occupation,
    }
