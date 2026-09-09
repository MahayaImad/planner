"""
Métriques de qualité d'un emploi du temps généré.

Un statut OPTIMAL du solveur ne dit rien de l'utilisabilité du résultat :
ces indicateurs mesurent ce qu'un directeur d'établissement regarde en
premier. Ils servent aussi de garde-fou dans les tests.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from .models import (
    APRES_MIDI, Classe, CoursRequis, GrilleHoraire, LeconPlanifiee,
    Matiere, Professeur, Salle,
)


@dataclass
class Metriques:
    lecons_placees: int = 0
    lecons_attendues: int = 0

    trous_classes: int = 0
    trous_professeurs: int = 0
    trous_doubles_professeurs: int = 0
    heures_isolees_professeurs: int = 0
    salles_empruntees_fouj: Dict[str, int] = field(default_factory=dict)
    seances_tardives_min: int = 0
    seances_tardives_max: int = 0
    seance_tardive: int = 6
    permanences: int = 0
    depassements_capacite: int = 0
    salles_specialisees_gaspillees: int = 0
    salles_par_classe: Dict[str, int] = field(default_factory=dict)
    max_matiere_par_jour: int = 0
    matiere_dispersee_dans_journee: int = 0
    charge_journaliere_min: int = 0
    charge_journaliere_max: int = 0
    jours_presence_professeurs: Dict[str, int] = field(default_factory=dict)
    seances_doubles: int = 0
    heures_lourdes_apres_midi: int = 0

    @property
    def complet(self) -> bool:
        return self.lecons_placees == self.lecons_attendues

    def resume(self) -> str:
        lignes = [
            f"Leçons placées                        : {self.lecons_placees}/{self.lecons_attendues}",
            f"Trous dans les journées des classes   : {self.trous_classes}",
            f"Trous dans les journées des profs     : {self.trous_professeurs}"
            f"  (dont vides de 2 h : {self.trous_doubles_professeurs})",
            f"Demi-journées à une seule heure (prof) : {self.heures_isolees_professeurs}",
            f"Heures de permanence attribuées       : {self.permanences}",
            f"Dépassements de capacité des salles   : {self.depassements_capacite}",
            f"Cours ordinaires en salle spécialisée : {self.salles_specialisees_gaspillees}",
            f"Salles fréquentées par classe         : "
            f"{min(self.salles_par_classe.values()) if self.salles_par_classe else 0}"
            f"–{max(self.salles_par_classe.values()) if self.salles_par_classe else 0}",
            f"Max h. d'une matière dans une journée : {self.max_matiere_par_jour}",
            f"Matière éclatée dans la journée       : {self.matiere_dispersee_dans_journee}",
            f"Charge journalière des classes        : "
            f"{self.charge_journaliere_min}h–{self.charge_journaliere_max}h",
            f"Jours de présence des professeurs     : "
            f"{min(self.jours_presence_professeurs.values()) if self.jours_presence_professeurs else 0}"
            f"–{max(self.jours_presence_professeurs.values()) if self.jours_presence_professeurs else 0}",
            f"Séances doubles constituées           : {self.seances_doubles // 2}",
            f"Séances 7 par classe (équité)         : "
            f"{self.seances_tardives_min}–{self.seances_tardives_max}",
            f"Salles empruntées pour les fouj       : "
            f"{min(self.salles_empruntees_fouj.values()) if self.salles_empruntees_fouj else 0}"
            f"–{max(self.salles_empruntees_fouj.values()) if self.salles_empruntees_fouj else 0}",
            f"Heures de matières lourdes l'après-midi: {self.heures_lourdes_apres_midi}",
        ]
        return "\n".join("  " + l for l in lignes)


def evaluer(
    lecons: Sequence[LeconPlanifiee],
    grille: GrilleHoraire,
    salles: Sequence[Salle],
    matieres: Sequence[Matiere],
    professeurs: Sequence[Professeur],
    classes: Sequence[Classe],
    cours_requis: Sequence[CoursRequis],
    type_salle_ordinaire: str = "classique",
) -> Metriques:
    idx_creneaux = grille.index()
    idx_salles = {s.id: s for s in salles}
    idx_matieres = {m.id: m for m in matieres}
    idx_profs = {p.id: p for p in professeurs}
    idx_classes = {c.id: c for c in classes}
    idx_cours = {cr.id: cr for cr in cours_requis}

    m = Metriques(
        lecons_placees=len(lecons),
        lecons_attendues=sum(cr.heures_par_semaine for cr in cours_requis),
    )

    # Occupation de la classe : un fouj mobilise deux enseignants et
    # deux salles sur le MÊME créneau — la classe n'y est occupée
    # qu'une fois. Toutes les mesures côté élèves dédoublonnent donc
    # par créneau, sans quoi les trous et les charges sont faussés.
    occ_classe = defaultdict(set)     # (classe, jour, demi) → {index}
    occ_prof = defaultdict(set)
    salles_vues = defaultdict(set)          # hors fouj : salle attitrée
    salles_fouj = defaultdict(set)
    charge_jour = defaultdict(set)
    cours_jour = defaultdict(list)          # (cours_requis, jour) → [index]
    jours_prof = defaultdict(set)
    seances_tardives = defaultdict(int)

    for lecon in lecons:
        creneau = idx_creneaux[lecon.creneau_id]
        classe = idx_classes[lecon.classe_id]
        salle = idx_salles[lecon.salle_id]
        cr = idx_cours.get(lecon.cours_requis_id)

        occ_classe[(lecon.classe_id, creneau.jour, creneau.demi_journee)].add(
            creneau.index_demi_journee)
        occ_prof[(lecon.professeur_id, creneau.jour, creneau.demi_journee)].add(
            creneau.index_demi_journee)

        if cr and cr.couplage_id:
            salles_fouj[lecon.classe_id].add(lecon.salle_id)
        else:
            salles_vues[lecon.classe_id].add(lecon.salle_id)

        charge_jour[(lecon.classe_id, creneau.jour)].add(creneau.id)
        cours_jour[(lecon.cours_requis_id, creneau.jour)].append(
            creneau.index_dans_jour)
        jours_prof[lecon.professeur_id].add(creneau.jour)
        if creneau.index_seance == m.seance_tardive:
            seances_tardives[lecon.classe_id] += 1

        effectif = (cr.effectif if cr and cr.effectif
                    else (classe.effectif + 1) // 2 if cr and cr.couplage_id
                    else classe.effectif)
        if effectif > salle.capacite:
            m.depassements_capacite += 1

        type_requis = None
        if cr:
            type_requis = cr.type_salle_requis or idx_matieres[cr.matiere_id].type_salle_requis
        if (type_requis in (None, type_salle_ordinaire)
                and salle.type != type_salle_ordinaire):
            m.salles_specialisees_gaspillees += 1

        if lecon.en_seance_double:
            m.seances_doubles += 1
        if idx_matieres[lecon.matiere_id].prefere_matin and creneau.demi_journee == APRES_MIDI:
            m.heures_lourdes_apres_midi += 1

    def mesurer_trous(occupation):
        """Retourne (trous simples, trous de 2 h ou plus, heures isolées)."""
        simples = doubles = isolees = 0
        for indices in occupation.values():
            if len(indices) == 1:
                isolees += 1
                continue
            indices = sorted(indices)
            libres = [i for i in range(indices[0], indices[-1] + 1)
                      if i not in set(indices)]
            simples += len(libres)
            doubles += sum(1 for a, b in zip(libres, libres[1:]) if b == a + 1)
        return simples, doubles, isolees

    m.trous_classes, _, _ = mesurer_trous(occ_classe)
    m.trous_professeurs, m.trous_doubles_professeurs, m.heures_isolees_professeurs = \
        mesurer_trous(occ_prof)

    m.salles_par_classe = {
        idx_classes[cid].nom: len(v) for cid, v in salles_vues.items()
    }
    m.salles_empruntees_fouj = {
        idx_classes[cid].nom: len(v) for cid, v in salles_fouj.items()
    }
    if charge_jour:
        tailles = [len(v) for v in charge_jour.values()]
        m.charge_journaliere_min = min(tailles)
        m.charge_journaliere_max = max(tailles)

    for indices in cours_jour.values():
        m.max_matiere_par_jour = max(m.max_matiere_par_jour, len(indices))
        if len(indices) > 1:
            indices = sorted(indices)
            if indices[-1] - indices[0] + 1 != len(indices):
                m.matiere_dispersee_dans_journee += 1

    if seances_tardives:
        m.seances_tardives_min = min(seances_tardives.values())
        m.seances_tardives_max = max(seances_tardives.values())

    m.jours_presence_professeurs = {
        idx_profs[pid].nom_complet: len(v) for pid, v in jours_prof.items()
    }
    return m
