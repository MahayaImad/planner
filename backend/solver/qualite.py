"""
Métriques de qualité d'un emploi du temps généré.

Un statut OPTIMAL du solveur ne dit rien de l'utilisabilité du résultat :
ces indicateurs mesurent ce qu'un directeur d'établissement regarde en
premier. Ils servent aussi de garde-fou dans les tests.
"""

from collections import Counter, defaultdict
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
    # Journées où un enseignant subit plus d'une heure creuse.
    journees_hachees_professeurs: int = 0
    heures_creuses_en_trop: int = 0
    # Heures creuses vues sur la journée entière (pause déjeuner incluse
    # dans l'amplitude) : toujours ≥ trous_professeurs, qui les compte
    # par demi-journée.
    heures_creuses_journee: int = 0
    # Coupures séparées au-delà de la première, à titre indicatif.
    coupures_en_trop: int = 0
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
    # Nombre de journées-professeur par volume horaire : {5: 12, 6: 3}.
    charges_quotidiennes_professeurs: Dict[int, int] = field(default_factory=dict)
    # Nombre de journées-division par nombre de matières vues 2 h ou
    # plus dans la journée : {0: 18, 1: 35, 2: 37, 3: 10}.
    matieres_doublees_par_jour: Dict[int, int] = field(default_factory=dict)
    # Matières doublées au-delà de la première, cumulées sur la semaine.
    empilements_de_matieres: int = 0
    # Heures groupées au-delà de ce que la politique de blocs autorise.
    blocs_hors_politique: int = 0
    # Matières vues 3 h ou plus dans une même journée.
    matieres_a_trois_heures: int = 0
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
            f"Heures creuses vues sur la journée    : {self.heures_creuses_journee}",
            f"Journées à plus d'une heure creuse    : "
            f"{self.journees_hachees_professeurs}"
            f"  (heures en trop : {self.heures_creuses_en_trop},"
            f" coupures séparées en trop : {self.coupures_en_trop})",
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
            f"Charge quotidienne des professeurs    : "
            f"{self.charges_quotidiennes_professeurs}",
            f"Matières doublées par journée-division: "
            f"{self.matieres_doublees_par_jour}",
            f"Empilements de matières doublées      : "
            f"{self.empilements_de_matieres}",
            f"Heures groupées hors politique        : "
            f"{self.blocs_hors_politique}",
            f"Matières à 3 h dans la journée        : "
            f"{self.matieres_a_trois_heures}",
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
    # Occupation sur la journée entière, pour le critère de journée hachée.
    occ_prof_jour = defaultdict(set)
    salles_vues = defaultdict(set)          # hors fouj : salle attitrée
    salles_fouj = defaultdict(set)
    charge_jour = defaultdict(set)
    cours_jour = defaultdict(list)          # (cours_requis, jour) → [index]
    # (classe, matière, jour) → {créneaux} : le fouj occupe la division
    # une seule fois, on dédoublonne donc par créneau.
    matiere_jour = defaultdict(set)
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
        occ_prof_jour[(lecon.professeur_id, creneau.jour)].add(
            creneau.index_dans_jour)

        matiere_jour[(lecon.classe_id, lecon.matiere_id, creneau.jour)].add(
            creneau.id)

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

    # Coupures par journée : un trou le matin et un autre l'après-midi
    # font deux coupures dans la même journée, même si aucune des deux
    # demi-journées n'est trouée deux fois.
    # Journée entière, de la première à la dernière heure de cours. Une
    # séance libre juste avant le déjeuner suivie d'un cours l'après-midi
    # est bien une heure creuse pour l'enseignant, même si le découpage
    # en demi-journées ne la voit pas.
    creux_par_jour = defaultdict(int)
    coupures_par_jour = defaultdict(int)
    for (prof_id, jour), positions in occ_prof_jour.items():
        indices = sorted(positions)
        if len(indices) < 2:
            continue
        precedent_creux = False
        for i in range(indices[0], indices[-1] + 1):
            creux = i not in positions
            if creux:
                creux_par_jour[(prof_id, jour)] += 1
                if not precedent_creux:
                    coupures_par_jour[(prof_id, jour)] += 1
            precedent_creux = creux
    for cle, heures_creuses in creux_par_jour.items():
        m.heures_creuses_journee += heures_creuses
        if heures_creuses > 1:
            m.journees_hachees_professeurs += 1
            m.heures_creuses_en_trop += heures_creuses - 1
        m.coupures_en_trop += max(0, coupures_par_jour[cle] - 1)

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

    charges = Counter(len(positions) for positions in occ_prof_jour.values())
    m.charges_quotidiennes_professeurs = dict(sorted(charges.items()))

    # Répétition des matières : la politique de blocs du programme, lue
    # dans nb_seances_doubles, dit combien de journées doublées une
    # matière peut légitimement occuper dans la semaine.
    blocs_permis = defaultdict(int)
    porteurs = {}
    for cr in cours_requis:
        if cr.couplage_id:
            garde = porteurs.setdefault(cr.couplage_id, cr)
            if (cr.groupe or "", cr.id) < (garde.groupe or "", garde.id):
                porteurs[cr.couplage_id] = cr
    porteurs_ids = {cr.id for cr in porteurs.values()}
    for cr in cours_requis:
        if cr.couplage_id and cr.id not in porteurs_ids:
            continue
        blocs_permis[(cr.classe_id, cr.matiere_id)] += cr.nb_seances_doubles

    doublees_par_jour = defaultdict(int)
    surplus_semaine = defaultdict(int)
    jours_de_classe = set()
    for (classe_id, matiere_id, jour), creneaux in matiere_jour.items():
        jours_de_classe.add((classe_id, jour))
        heures = len(creneaux)
        if heures >= 2:
            doublees_par_jour[(classe_id, jour)] += 1
            surplus_semaine[(classe_id, matiere_id)] += heures - 1
        if heures >= 3:
            m.matieres_a_trois_heures += 1

    repartition = Counter(doublees_par_jour.get(cle, 0) for cle in jours_de_classe)
    m.matieres_doublees_par_jour = dict(sorted(repartition.items()))
    m.empilements_de_matieres = sum(max(0, n - 1)
                                    for n in doublees_par_jour.values())
    m.blocs_hors_politique = sum(
        max(0, surplus - blocs_permis[cle])
        for cle, surplus in surplus_semaine.items())

    m.jours_presence_professeurs = {
        idx_profs[pid].nom_complet: len(v) for pid, v in jours_prof.items()
    }
    return m
