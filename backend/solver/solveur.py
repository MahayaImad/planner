"""
Solveur CP-SAT pour la génération d'emplois du temps scolaires.

Contraintes modélisées :
  C1 - Un professeur ne peut pas être dans deux endroits simultanément
  C2 - Une classe ne peut avoir qu'un seul cours à la fois
  C3 - Une salle ne peut accueillir qu'un seul cours à la fois
  C4 - Un professeur n'est planifié que sur ses créneaux disponibles
  C5 - Le nombre d'heures requis par matière/classe est respecté
  C6 - Un prof ne dépasse pas son nombre max d'heures consécutives
"""

from typing import List, Dict, Tuple, Optional
from ortools.sat.python import cp_model

from .models import (
    Creneau, Salle, Matiere, Professeur,
    Classe, CoursRequis, LeconPlanifiee
)


class SolveurEmploiDuTemps:

    def __init__(
        self,
        creneaux: List[Creneau],
        salles: List[Salle],
        matieres: List[Matiere],
        professeurs: List[Professeur],
        classes: List[Classe],
        cours_requis: List[CoursRequis],
        limite_secondes: int = 60,
    ):
        self.creneaux = creneaux
        self.salles = salles
        self.matieres = matieres
        self.professeurs = professeurs
        self.classes = classes
        self.cours_requis = cours_requis
        self.limite_secondes = limite_secondes

        # Index rapides
        self._idx_creneaux = {c.id: c for c in creneaux}
        self._idx_salles = {s.id: s for s in salles}
        self._idx_matieres = {m.id: m for m in matieres}
        self._idx_professeurs = {p.id: p for p in professeurs}
        self._idx_classes = {cl.id: cl for cl in classes}

        # Regrouper les créneaux par jour pour C6
        self._creneaux_par_jour: Dict[str, List[int]] = {}
        for c in creneaux:
            self._creneaux_par_jour.setdefault(c.jour, []).append(c.id)

    # ------------------------------------------------------------------
    def resoudre(self) -> Tuple[str, List[LeconPlanifiee]]:
        """
        Lance le solveur.
        Retourne (statut, liste_de_leçons).
        statut : "OPTIMAL" | "FEASIBLE" | "INFEASIBLE" | "UNKNOWN"
        """
        modele = cp_model.CpModel()

        # ----------------------------------------------------------------
        # Variables de décision
        # x[cr_id, salle_id, creneau_id] = 1 si le cours requis cr est
        # planifié dans cette salle à ce créneau.
        # ----------------------------------------------------------------
        x: Dict[Tuple[int, int, int], cp_model.IntVar] = {}

        for cr in self.cours_requis:
            prof = self._idx_professeurs[cr.professeur_id]
            for salle in self.salles:
                # Filtrer : type de salle compatible
                if cr.type_salle_requis and salle.type != cr.type_salle_requis:
                    continue
                for creneau in self.creneaux:
                    # Filtrer : prof disponible sur ce créneau
                    if (prof.creneaux_disponibles
                            and creneau.id not in prof.creneaux_disponibles):
                        continue
                    var = modele.NewBoolVar(
                        f"x_cr{cr.id}_s{salle.id}_t{creneau.id}"
                    )
                    x[(cr.id, salle.id, creneau.id)] = var

        # ----------------------------------------------------------------
        # C5 — Chaque cours requis doit être planifié exactement
        #       heures_par_semaine fois.
        # ----------------------------------------------------------------
        for cr in self.cours_requis:
            vars_cr = [
                v for (cr_id, _, __), v in x.items() if cr_id == cr.id
            ]
            if not vars_cr:
                # Impossible de planifier ce cours → le problème est infaisable
                modele.Add(cp_model.LinearExpr.Sum([]) == cr.heures_par_semaine)
            else:
                modele.Add(
                    cp_model.LinearExpr.Sum(vars_cr) == cr.heures_par_semaine
                )

        # ----------------------------------------------------------------
        # C1 — Un professeur ne peut pas avoir deux cours simultanément.
        # ----------------------------------------------------------------
        for prof in self.professeurs:
            cours_du_prof = [cr for cr in self.cours_requis
                             if cr.professeur_id == prof.id]
            for creneau in self.creneaux:
                vars_prof_creneau = [
                    v for (cr_id, _, t_id), v in x.items()
                    if t_id == creneau.id
                    and any(cr.id == cr_id for cr in cours_du_prof)
                ]
                if len(vars_prof_creneau) > 1:
                    modele.Add(
                        cp_model.LinearExpr.Sum(vars_prof_creneau) <= 1
                    )

        # ----------------------------------------------------------------
        # C2 — Une classe ne peut pas avoir deux cours simultanément.
        # ----------------------------------------------------------------
        for classe in self.classes:
            cours_de_la_classe = [cr for cr in self.cours_requis
                                  if cr.classe_id == classe.id]
            for creneau in self.creneaux:
                vars_classe_creneau = [
                    v for (cr_id, _, t_id), v in x.items()
                    if t_id == creneau.id
                    and any(cr.id == cr_id for cr in cours_de_la_classe)
                ]
                if len(vars_classe_creneau) > 1:
                    modele.Add(
                        cp_model.LinearExpr.Sum(vars_classe_creneau) <= 1
                    )

        # ----------------------------------------------------------------
        # C3 — Une salle ne peut accueillir qu'un seul cours à la fois.
        # ----------------------------------------------------------------
        for salle in self.salles:
            for creneau in self.creneaux:
                vars_salle_creneau = [
                    v for (_, s_id, t_id), v in x.items()
                    if s_id == salle.id and t_id == creneau.id
                ]
                if len(vars_salle_creneau) > 1:
                    modele.Add(
                        cp_model.LinearExpr.Sum(vars_salle_creneau) <= 1
                    )

        # ----------------------------------------------------------------
        # C6 — Pas plus de max_heures_consecutives pour un prof par jour.
        # ----------------------------------------------------------------
        for prof in self.professeurs:
            cours_du_prof = [cr for cr in self.cours_requis
                             if cr.professeur_id == prof.id]
            max_consec = prof.max_heures_consecutives

            for jour, ids_creneaux_jour in self._creneaux_par_jour.items():
                # Trier les créneaux du jour par heure de début
                creneaux_du_jour = sorted(
                    [self._idx_creneaux[tid] for tid in ids_creneaux_jour],
                    key=lambda c: c.heure_debut
                )
                n = len(creneaux_du_jour)
                if n <= max_consec:
                    continue  # pas assez de créneaux pour violer la contrainte

                for debut in range(n - max_consec):
                    fenetre = creneaux_du_jour[debut:debut + max_consec + 1]
                    vars_fenetre = [
                        v for (cr_id, _, t_id), v in x.items()
                        if t_id in {c.id for c in fenetre}
                        and any(cr.id == cr_id for cr in cours_du_prof)
                    ]
                    if len(vars_fenetre) > max_consec:
                        modele.Add(
                            cp_model.LinearExpr.Sum(vars_fenetre) <= max_consec
                        )

        # ----------------------------------------------------------------
        # Résolution
        # ----------------------------------------------------------------
        solveur = cp_model.CpSolver()
        solveur.parameters.max_time_in_seconds = self.limite_secondes
        solveur.parameters.log_search_progress = False

        statut = solveur.Solve(modele)
        statut_str = solveur.StatusName(statut)

        lecons: List[LeconPlanifiee] = []

        if statut in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for (cr_id, salle_id, creneau_id), var in x.items():
                if solveur.Value(var) == 1:
                    cr = next(c for c in self.cours_requis if c.id == cr_id)
                    lecons.append(LeconPlanifiee(
                        cours_requis_id=cr_id,
                        classe_id=cr.classe_id,
                        matiere_id=cr.matiere_id,
                        professeur_id=cr.professeur_id,
                        salle_id=salle_id,
                        creneau_id=creneau_id,
                    ))

        return statut_str, lecons
