"""
Solveur CP-SAT pour la génération d'emplois du temps scolaires.

Modèle
──────
Le placement est décomposé en deux couches, au lieu d'une seule
variable (cours, salle, créneau) :

  y[cr, t]      le cours requis « cr » occupe le créneau « t »
  w[cr, t, s]   ... dans la salle « s »   (créée uniquement lorsque
                plusieurs salles sont possibles)

Comme une classe a une salle attitrée, la grande majorité des heures
n'a qu'une seule salle possible : la variable de salle disparaît. Sur
un CEM de 12 classes cela divise le nombre de variables par ~14 et
supprime la symétrie entre salles interchangeables.

Contraintes DURES
  D1  volume horaire hebdomadaire respecté
  D2  une classe suit au plus un cours à la fois
  D3  un professeur assure au plus un cours à la fois
  D4  une salle accueille au plus un cours à la fois
  D5  professeur placé uniquement sur ses créneaux de disponibilité
  D6  salle compatible : type requis, capacité, salle attitrée
  D7  heures consécutives d'un professeur plafonnées (par demi-journée)
  D8  heures quotidiennes plafonnées (professeur et classe)
  D9  répartition : plafond d'heures d'une matière par jour
  D10 séances doubles : N blocs de 2 h accolées, même salle
  D11 regroupement : 2 h d'une matière le même jour sont accolées
  D12 aucune heure de trou dans la journée d'une classe
  D13 jours de présence d'un professeur plafonnés
  D14 demi-journées travaillées d'une classe plafonnées

Contraintes SOUPLES (fonction objectif pondérée)
  S1  minimiser les heures de trou des professeurs
  S2  minimiser le nombre de jours de présence des professeurs
  S3  placer les matières lourdes le matin
  S4  équilibrer la charge quotidienne des classes
  S5  minimiser les demi-journées travaillées par les classes
"""

import logging
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ortools.sat.python import cp_model

from .diagnostic import ERREUR, diagnostiquer
from .models import (
    APRES_MIDI, Classe, CoursRequis, Creneau, FenetrePedagogique, GrilleHoraire,
    LeconPlanifiee, Matiere, Options, Ponderations, Professeur, Resultat, Salle,
)

logger = logging.getLogger(__name__)


class _SuiviRecherche(cp_model.CpSolverSolutionCallback):
    """
    Suit la recherche : remonte chaque solution améliorante et permet de
    l'interrompre proprement.

    Une génération dure plusieurs minutes. Sans point d'arrêt, la seule
    façon de la stopper serait de tuer le processus — ce qui laisserait
    la tâche en base dans un état incohérent.
    """

    def __init__(self, rappel=None, arret=None):
        super().__init__()
        self._rappel = rappel
        self._arret = arret
        self.nb_solutions = 0

    def on_solution_callback(self):
        self.nb_solutions += 1
        if self._rappel is not None:
            try:
                self._rappel(int(self.ObjectiveValue()), self.WallTime())
            except Exception:
                # Le suivi ne doit jamais faire échouer la résolution,
                # mais une panne silencieuse serait pire : la tracer.
                logger.warning("Rappel de progression en échec", exc_info=True)
        if self._arret is not None and self._arret():
            self.StopSearch()


class SolveurEmploiDuTemps:

    def __init__(
        self,
        grille: Optional[GrilleHoraire] = None,
        salles: Sequence[Salle] = (),
        matieres: Sequence[Matiere] = (),
        professeurs: Sequence[Professeur] = (),
        classes: Sequence[Classe] = (),
        cours_requis: Sequence[CoursRequis] = (),
        fenetres_pedagogiques: Sequence["FenetrePedagogique"] = (),
        options: Optional[Options] = None,
        ponderations: Optional[Ponderations] = None,
        creneaux: Optional[Sequence[Creneau]] = None,
        limite_secondes: Optional[int] = None,
    ):
        if grille is None:
            if creneaux is None:
                raise ValueError("Fournissez une GrilleHoraire ou une liste de créneaux.")
            grille = GrilleHoraire.depuis_creneaux(creneaux)

        self.grille = grille
        self.salles = list(salles)
        self.matieres = list(matieres)
        self.professeurs = list(professeurs)
        self.classes = list(classes)
        self.cours_requis = list(cours_requis)
        self.fenetres_pedagogiques = list(fenetres_pedagogiques)
        self.options = options or Options()
        self.ponderations = ponderations or Ponderations()
        if limite_secondes is not None:
            self.options.limite_secondes = limite_secondes

        self._salles = {s.id: s for s in self.salles}
        self._matieres = {m.id: m for m in self.matieres}
        self._professeurs = {p.id: p for p in self.professeurs}
        self._classes = {c.id: c for c in self.classes}
        self._creneaux = self.grille.index()
        self._par_jour = self.grille.par_jour()
        self._par_demi_journee = self.grille.par_demi_journee()

        # Fouj : cours donnés simultanément à deux demi-groupes.
        # Le premier cours du groupe « porte » l'occupation de la classe.
        self._couplages: Dict[str, List[CoursRequis]] = defaultdict(list)
        for cr in self.cours_requis:
            if cr.couplage_id:
                self._couplages[cr.couplage_id].append(cr)
        # Le « porteur » d'un fouj est le demi-groupe qui reste dans la
        # salle attitrée de la classe ; l'autre est accueilli ailleurs.
        # Le choix suit l'étiquette de groupe (G1 avant G2), pas
        # l'identifiant interne : il ne doit pas dépendre de l'ordre
        # dans lequel les cours ont été créés.
        self._porteur_couplage = {
            cle: min(groupe, key=lambda c: (c.groupe or "", c.id)).id
            for cle, groupe in self._couplages.items()
        }

        # Fenêtres pédagogiques → créneaux interdits par matière.
        self._interdits_matiere: Dict[int, set] = defaultdict(set)
        for fenetre in self.fenetres_pedagogiques:
            for creneau in self.grille.creneaux:
                if (creneau.index_jour == fenetre.index_jour
                        and creneau.index_seance in fenetre.seances_bloquees):
                    self._interdits_matiere[fenetre.matiere_id].add(creneau.id)

    # ══════════════════════════════════════════════════════════════
    #  Salles possibles pour un cours
    # ══════════════════════════════════════════════════════════════

    def _salles_possibles(self, cr: CoursRequis) -> List[int]:
        classe = self._classes[cr.classe_id]
        matiere = self._matieres[cr.matiere_id]
        type_requis = cr.type_salle_requis or matiere.type_salle_requis
        if type_requis == self.options.type_salle_ordinaire:
            type_requis = None      # salle ordinaire : pas une spécialité
        effectif = self._effectif(cr)

        if type_requis:
            candidates = [s for s in self.salles if s.type == type_requis]
        else:
            # Cours ordinaire : la classe reste dans sa salle attitrée.
            # Exception : le second demi-groupe d'un fouj doit être
            # accueilli ailleurs — typiquement la salle d'une division
            # partie au laboratoire, au stade ou en informatique.
            if (self.options.salle_attitree and classe.salle_attitree_id
                    and not self._est_partenaire_fouj(cr)):
                return [classe.salle_attitree_id]
            candidates = [
                s for s in self.salles
                if not self.options.reserver_salles_specialisees
                or s.type == self.options.type_salle_ordinaire
            ]

        if self.options.verifier_capacite_salle:
            assez_grandes = [s for s in candidates if s.capacite >= effectif]
            # Ne jamais rendre le problème infaisable sur ce seul critère :
            # le diagnostic a déjà signalé le sous-dimensionnement.
            if assez_grandes:
                candidates = assez_grandes
        return [s.id for s in candidates]

    def _est_partenaire_fouj(self, cr: CoursRequis) -> bool:
        """Vrai pour le demi-groupe d'un fouj qui doit sortir de sa salle."""
        return bool(cr.couplage_id) and self._porteur_couplage[cr.couplage_id] != cr.id

    def _effectif(self, cr: CoursRequis) -> int:
        if cr.effectif:
            return cr.effectif
        classe = self._classes[cr.classe_id]
        # Un cours de fouj ne reçoit qu'un demi-groupe.
        if cr.couplage_id:
            return (classe.effectif + 1) // 2
        return classe.effectif

    def _interdit(self, cr: CoursRequis, creneau_id: int) -> bool:
        return (creneau_id in self._interdits_matiere.get(cr.matiere_id, ())
                or creneau_id in cr.creneaux_interdits)

    # ══════════════════════════════════════════════════════════════
    #  Résolution
    # ══════════════════════════════════════════════════════════════

    def resoudre(
        self,
        rappel: Optional[Callable[[int, float], None]] = None,
        arret: Optional[Callable[[], bool]] = None,
    ) -> Resultat:
        """
        Monte le modèle et lance la recherche.

        rappel  appelé à chaque solution améliorante, avec le coût courant
                et le temps écoulé — sert à afficher la progression.
        arret   consulté à chaque solution ; renvoyer True interrompt la
                recherche et marque le résultat comme interrompu.
        """
        depart = time.perf_counter()

        anomalies = diagnostiquer(
            self.grille, self.salles, self.matieres, self.professeurs,
            self.classes, self.cours_requis, self.options,
            self.fenetres_pedagogiques,
        )
        bloquantes = [m for n, m in anomalies if n == ERREUR]
        if bloquantes:
            return Resultat(statut="INFEASIBLE", anomalies=anomalies,
                            duree_construction=time.perf_counter() - depart)

        modele = cp_model.CpModel()

        # ── Variables ─────────────────────────────────────────────
        y: Dict[Tuple[int, int], cp_model.IntVar] = {}
        w: Dict[Tuple[int, int, int], cp_model.IntVar] = {}
        salles_par_cours: Dict[int, List[int]] = {}

        # Index construits en une passe — c'est ce qui remplace les
        # balayages répétés du dictionnaire de variables.
        occ_classe: Dict[Tuple[int, int], List] = defaultdict(list)
        occ_prof: Dict[Tuple[int, int], List] = defaultdict(list)
        occ_salle: Dict[Tuple[int, int], List] = defaultdict(list)
        y_par_cours: Dict[int, List] = defaultdict(list)
        y_cours_jour: Dict[Tuple[int, str], List] = defaultdict(list)

        for cr in self.cours_requis:
            prof = self._professeurs[cr.professeur_id]
            possibles = self._salles_possibles(cr)
            salles_par_cours[cr.id] = possibles

            porteur = (self._porteur_couplage.get(cr.couplage_id)
                       if cr.couplage_id else cr.id)

            for creneau in self.grille.creneaux:
                if not prof.est_disponible(creneau.id):
                    continue
                if self._interdit(cr, creneau.id):
                    continue
                var = modele.NewBoolVar(f"y_c{cr.id}_t{creneau.id}")
                y[(cr.id, creneau.id)] = var
                y_par_cours[cr.id].append(var)
                y_cours_jour[(cr.id, creneau.jour)].append(var)
                occ_prof[(cr.professeur_id, creneau.id)].append(var)
                # Les deux demi-groupes d'un fouj n'occupent la classe
                # qu'une seule fois : seul le cours porteur la déclare.
                if porteur == cr.id:
                    occ_classe[(cr.classe_id, creneau.id)].append(var)

                if len(possibles) == 1:
                    occ_salle[(possibles[0], creneau.id)].append(var)
                else:
                    vars_salle = []
                    for salle_id in possibles:
                        v = modele.NewBoolVar(f"w_c{cr.id}_t{creneau.id}_s{salle_id}")
                        w[(cr.id, creneau.id, salle_id)] = v
                        vars_salle.append(v)
                        occ_salle[(salle_id, creneau.id)].append(v)
                    # D6 — exactement une salle si le cours a lieu.
                    modele.Add(sum(vars_salle) == var)

        # ── D1 — volume horaire hebdomadaire ──────────────────────
        for cr in self.cours_requis:
            modele.Add(sum(y_par_cours[cr.id]) == cr.heures_par_semaine)

        # ── D15 — fouj : les demi-groupes suivent le même créneau ──
        for cle, groupe in self._couplages.items():
            porteur_id = self._porteur_couplage[cle]
            porteur = next(c for c in groupe if c.id == porteur_id)
            for cr in groupe:
                if cr.id == porteur_id:
                    continue
                for creneau in self.grille.creneaux:
                    a = y.get((porteur.id, creneau.id))
                    b = y.get((cr.id, creneau.id))
                    if a is None and b is None:
                        continue
                    if a is None:
                        modele.Add(b == 0)
                    elif b is None:
                        modele.Add(a == 0)
                    else:
                        modele.Add(a == b)

        # ── D2/D3 — occupation exclusive, réifiée ─────────────────
        # Les booléens d'occupation servent aussi aux trous et à la charge.
        b_classe: Dict[Tuple[int, int], cp_model.IntVar] = {}
        for classe in self.classes:
            for creneau in self.grille.creneaux:
                cle = (classe.id, creneau.id)
                variables = occ_classe.get(cle)
                if not variables:
                    continue
                b = modele.NewBoolVar(f"occ_cl{classe.id}_t{creneau.id}")
                modele.Add(sum(variables) == b)  # ≤ 1 implicite
                b_classe[cle] = b

        # Défini sur TOUS les créneaux ouverts, y compris ceux où le
        # professeur n'a aucun cours possible : le calcul des trous a
        # besoin d'une valeur d'occupation à chaque position.
        b_prof: Dict[Tuple[int, int], cp_model.IntVar] = {}
        for prof in self.professeurs:
            for creneau in self.grille.creneaux:
                cle = (prof.id, creneau.id)
                variables = occ_prof.get(cle)
                b = modele.NewBoolVar(f"occ_p{prof.id}_t{creneau.id}")
                if variables:
                    modele.Add(sum(variables) == b)
                else:
                    modele.Add(b == 0)
                b_prof[cle] = b

        # ── D4 — une salle, un cours ──────────────────────────────
        for (salle_id, creneau_id), variables in occ_salle.items():
            if len(variables) > 1:
                modele.Add(sum(variables) <= 1)

        # ── D9 — répartition d'une matière dans la semaine ────────
        for cr in self.cours_requis:
            for jour in self.grille.jours:
                variables = y_cours_jour.get((cr.id, jour))
                if variables and len(variables) > cr.max_heures_par_jour:
                    modele.Add(sum(variables) <= cr.max_heures_par_jour)

        # ── D10 — séances doubles ─────────────────────────────────
        paires = self.grille.paires_consecutives()
        doubles_par_cours: Dict[int, List] = defaultdict(list)
        doubles_par_cours_jour: Dict[Tuple[int, str], List] = defaultdict(list)
        d_vars: Dict[Tuple[int, int], cp_model.IntVar] = {}

        besoin_doubles = any(cr.nb_seances_doubles for cr in self.cours_requis)
        if besoin_doubles or self.options.grouper_matiere_meme_jour:
            for cr in self.cours_requis:
                if cr.heures_par_semaine < 2:
                    continue
                for t1, t2 in paires:
                    v1, v2 = y.get((cr.id, t1)), y.get((cr.id, t2))
                    if v1 is None or v2 is None:
                        continue
                    d = modele.NewBoolVar(f"d_c{cr.id}_t{t1}")
                    modele.AddImplication(d, v1)
                    modele.AddImplication(d, v2)
                    d_vars[(cr.id, t1)] = d
                    doubles_par_cours[cr.id].append(d)
                    doubles_par_cours_jour[(cr.id, self._creneaux[t1].jour)].append(d)
                    # Même salle sur les deux heures du bloc.
                    for salle_id in salles_par_cours[cr.id]:
                        a = w.get((cr.id, t1, salle_id))
                        b = w.get((cr.id, t2, salle_id))
                        if a is not None and b is not None:
                            modele.Add(a == b).OnlyEnforceIf(d)

            for cr in self.cours_requis:
                if cr.nb_seances_doubles:
                    modele.Add(sum(doubles_par_cours[cr.id]) >= cr.nb_seances_doubles)

        # ── D11 — 2 h d'une matière le même jour ⇒ accolées ───────
        if self.options.grouper_matiere_meme_jour:
            for cr in self.cours_requis:
                if cr.max_heures_par_jour < 2 or cr.heures_par_semaine < 2:
                    continue
                for jour in self.grille.jours:
                    variables = y_cours_jour.get((cr.id, jour))
                    if not variables or len(variables) < 2:
                        continue
                    blocs = doubles_par_cours_jour.get((cr.id, jour), [])
                    if blocs:
                        modele.Add(sum(variables) <= 1 + sum(blocs))

        # ── D7/D8/D13 — contraintes de service des professeurs ────
        for prof in self.professeurs:
            # D17 : service hebdomadaire plafonné.
            if prof.max_heures_par_semaine is not None:
                semaine = [b_prof[(prof.id, c.id)] for c in self.grille.creneaux
                           if (prof.id, c.id) in b_prof]
                if len(semaine) > prof.max_heures_par_semaine:
                    modele.Add(sum(semaine) <= prof.max_heures_par_semaine)

            # D7 : heures consécutives, à l'intérieur d'une demi-journée.
            fenetre = prof.max_heures_consecutives
            for creneaux_dj in self._par_demi_journee.values():
                ids = [c.id for c in creneaux_dj]
                if len(ids) <= fenetre:
                    continue
                for debut in range(len(ids) - fenetre):
                    bloc = [b_prof[(prof.id, t)] for t in ids[debut:debut + fenetre + 1]
                            if (prof.id, t) in b_prof]
                    if len(bloc) > fenetre:
                        modele.Add(sum(bloc) <= fenetre)

            # D8 : heures par jour.
            jours_travailles = []
            for jour, creneaux_j in self._par_jour.items():
                du_jour = [b_prof[(prof.id, c.id)] for c in creneaux_j
                           if (prof.id, c.id) in b_prof]
                if not du_jour:
                    continue
                if len(du_jour) > prof.max_heures_par_jour:
                    modele.Add(sum(du_jour) <= prof.max_heures_par_jour)
                present = modele.NewBoolVar(f"jour_p{prof.id}_{jour}")
                modele.AddMaxEquality(present, du_jour)
                jours_travailles.append(present)
            self._jours_prof = getattr(self, "_jours_prof", {})
            self._jours_prof[prof.id] = jours_travailles

            # D13 : nombre de jours de présence.
            if prof.max_jours_presence is not None and jours_travailles:
                modele.Add(sum(jours_travailles) <= prof.max_jours_presence)

        # ── D8/D12/D14 — journées des classes ─────────────────────
        charges_classe: Dict[int, List] = defaultdict(list)
        demi_journees_classe: Dict[int, List] = defaultdict(list)

        for classe in self.classes:
            for jour, creneaux_j in self._par_jour.items():
                du_jour = [b_classe[(classe.id, c.id)] for c in creneaux_j
                           if (classe.id, c.id) in b_classe]
                if not du_jour:
                    continue
                charge = modele.NewIntVar(0, classe.max_heures_par_jour,
                                          f"charge_cl{classe.id}_{jour}")
                modele.Add(charge == sum(du_jour))
                charges_classe[classe.id].append(charge)

            for (jour, demi), creneaux_dj in self._par_demi_journee.items():
                occupees = [b_classe[(classe.id, c.id)] for c in creneaux_dj
                            if (classe.id, c.id) in b_classe]
                if not occupees:
                    continue

                travaillee = modele.NewBoolVar(f"dj_cl{classe.id}_{jour}_{demi}")
                modele.AddMaxEquality(travaillee, occupees)
                demi_journees_classe[classe.id].append(travaillee)

                # D12 : pas de trou — interdit le motif occupé/libre/occupé.
                if self.options.zero_trou_classes:
                    n = len(occupees)
                    for i in range(n):
                        for k in range(i + 2, n):
                            for j in range(i + 1, k):
                                modele.Add(
                                    occupees[i] + occupees[k] - occupees[j] <= 1
                                )

            # D14 : demi-journées travaillées plafonnées.
            if classe.max_demi_journees is not None and demi_journees_classe[classe.id]:
                modele.Add(sum(demi_journees_classe[classe.id]) <= classe.max_demi_journees)

        # ── D16 — présence minimale d'une classe par demi-journée ──
        for nom_shift, minimum in self.options.presence_minimale.items():
            if minimum <= 0:
                continue
            for classe in self.classes:
                for (jour, demi), creneaux_dj in self._par_demi_journee.items():
                    if demi != nom_shift:
                        continue
                    occupees = [b_classe[(classe.id, c.id)] for c in creneaux_dj
                                if (classe.id, c.id) in b_classe]
                    if len(occupees) >= minimum:
                        modele.Add(sum(occupees) >= minimum)

        # ══════════════════════════════════════════════════════════
        #  Fonction objectif
        # ══════════════════════════════════════════════════════════
        termes = []
        permanences: Dict[Tuple[int, int], cp_model.IntVar] = {}
        p = self.ponderations

        # ── S1..S3, S6 — service des professeurs, demi-journée par
        #    demi-journée : trous, vides de 2 h, heure isolée, permanences.
        besoin_service = any((
            p.trous_professeurs, p.trous_doubles_professeurs,
            p.heure_isolee_professeur, p.recompense_permanence,
            p.journee_hachee_professeur,
        ))
        if besoin_service:
            for prof in self.professeurs:
                permanences_prof = []
                # Débuts de trou, regroupés par JOUR : un trou le matin et
                # un autre l'après-midi font bien deux coupures dans la
                # même journée.
                debuts_par_jour: Dict[str, List] = defaultdict(list)
                for (jour, demi), creneaux_dj in self._par_demi_journee.items():
                    occ = [b_prof[(prof.id, c.id)] for c in creneaux_dj]
                    n = len(occ)
                    if n < 2:
                        continue

                    presente = modele.NewBoolVar(f"pres_p{prof.id}_{jour}_{demi}")
                    modele.AddMaxEquality(presente, occ)
                    heures = sum(occ)

                    # S3 — professeur qui ne vient que pour une heure.
                    if (p.heure_isolee_professeur
                            and self.options.mode_heure_isolee == "PER_SHIFT"):
                        isolee = modele.NewBoolVar(f"iso_p{prof.id}_{jour}_{demi}")
                        modele.Add(heures == 1).OnlyEnforceIf(isolee)
                        modele.Add(heures != 1).OnlyEnforceIf(isolee.Not())
                        termes.append(p.heure_isolee_professeur * isolee)

                    if not (p.trous_professeurs or p.trous_doubles_professeurs
                            or p.recompense_permanence
                            or p.journee_hachee_professeur):
                        continue

                    # Amplitude de présence : de la première à la dernière heure.
                    debut_v = modele.NewIntVar(0, n - 1, f"deb_p{prof.id}_{jour}_{demi}")
                    fin_v = modele.NewIntVar(0, n - 1, f"fin_p{prof.id}_{jour}_{demi}")
                    for i, var in enumerate(occ):
                        modele.Add(debut_v <= i).OnlyEnforceIf(var)
                        modele.Add(fin_v >= i).OnlyEnforceIf(var)

                    # Une séance est un trou si elle est DANS l'amplitude
                    # de présence et pourtant libre.
                    trous = []
                    for i, var in enumerate(occ):
                        apres_debut = modele.NewBoolVar("")
                        modele.Add(debut_v <= i).OnlyEnforceIf(apres_debut)
                        modele.Add(debut_v >= i + 1).OnlyEnforceIf(apres_debut.Not())
                        avant_fin = modele.NewBoolVar("")
                        modele.Add(fin_v >= i).OnlyEnforceIf(avant_fin)
                        modele.Add(fin_v <= i - 1).OnlyEnforceIf(avant_fin.Not())

                        trou = modele.NewBoolVar(f"trou_p{prof.id}_{jour}_{demi}_{i}")
                        modele.AddBoolAnd([apres_debut, avant_fin, var.Not()]
                                          ).OnlyEnforceIf(trou)
                        modele.AddBoolOr([apres_debut.Not(), avant_fin.Not(), var]
                                         ).OnlyEnforceIf(trou.Not())
                        trous.append(trou)
                        if p.trous_professeurs:
                            termes.append(p.trous_professeurs * trou)

                        # S6 — permanence : un trou comblé par de l'accueil
                        # ou de l'étude surveillée reste du temps utile.
                        # Seuls les enseignants qui en assurent y sont éligibles.
                        if p.recompense_permanence and prof.assure_permanences:
                            creneau = creneaux_dj[i]
                            perm = modele.NewBoolVar(
                                f"perm_p{prof.id}_t{creneau.id}")
                            modele.AddImplication(perm, trou)
                            permanences[(prof.id, creneau.id)] = perm
                            permanences_prof.append(perm)
                            termes.append(-p.recompense_permanence * perm)

                    # S2 — un vide de deux heures d'affilée coûte bien plus
                    # cher que deux trous isolés.
                    if p.trous_doubles_professeurs:
                        for a, b in zip(trous, trous[1:]):
                            double = modele.NewBoolVar("")
                            modele.Add(double >= a + b - 1)
                            termes.append(p.trous_doubles_professeurs * double)

                    # S11 — début d'une coupure : une séance creuse qui ne
                    # suit pas une autre séance creuse ouvre un nouveau
                    # trou. Les compter donne le nombre de coupures de la
                    # journée, indépendamment de leur longueur.
                    if p.journee_hachee_professeur:
                        for i, trou in enumerate(trous):
                            debut_trou = modele.NewBoolVar(
                                f"deb_trou_p{prof.id}_{jour}_{demi}_{i}")
                            if i == 0:
                                modele.Add(debut_trou >= trou)
                            else:
                                modele.Add(debut_trou >= trou - trous[i - 1])
                            debuts_par_jour[jour].append(debut_trou)

                # S11 — journée hachée. Le premier trou de la journée est
                # déjà facturé par S1 ; chaque coupure supplémentaire
                # ajoute ce surcoût.
                if p.journee_hachee_professeur:
                    for jour, debuts in debuts_par_jour.items():
                        if len(debuts) < 2:
                            continue
                        surplus = modele.NewIntVar(
                            0, len(debuts), f"hachee_p{prof.id}_{jour}")
                        modele.Add(surplus >= sum(debuts) - 1)
                        termes.append(p.journee_hachee_professeur * surplus)

                if permanences_prof and self.options.permanences_max_par_prof is not None:
                    modele.Add(sum(permanences_prof)
                               <= self.options.permanences_max_par_prof)

        # ── S4 — jours de présence des professeurs ────────────────
        if p.jours_presence_professeurs:
            for jours in getattr(self, "_jours_prof", {}).values():
                for present in jours:
                    termes.append(p.jours_presence_professeurs * present)

        # ── S5 — matières lourdes le matin ────────────────────────
        if p.matieres_lourdes_apres_midi:
            creneaux_pm = {c.id for c in self.grille.creneaux
                           if c.demi_journee == APRES_MIDI}
            for cr in self.cours_requis:
                if not self._matieres[cr.matiere_id].prefere_matin:
                    continue
                for t in creneaux_pm:
                    var = y.get((cr.id, t))
                    if var is not None:
                        termes.append(p.matieres_lourdes_apres_midi * var)

        # ── S7 — heure de sortie des élèves ───────────────────────
        # Coût croissant des dernières séances de la journée.
        if p.penalites_seance:
            for creneau in self.grille.creneaux:
                poids = p.penalites_seance.get(creneau.index_seance, 0)
                if not poids:
                    continue
                for classe in self.classes:
                    var = b_classe.get((classe.id, creneau.id))
                    if var is not None:
                        termes.append(poids * var)

        # ── S8 — équité des fins de journée entre divisions ───────
        # Sans ce terme, le solveur concentre toutes les sorties tardives
        # sur les mêmes classes : le coût total serait identique.
        if p.equite_derniere_seance:
            creneaux_tardifs = [c for c in self.grille.creneaux
                                if c.index_seance == p.seance_soumise_a_equite]
            if creneaux_tardifs:
                compteurs = []
                for classe in self.classes:
                    variables = [b_classe[(classe.id, c.id)] for c in creneaux_tardifs
                                 if (classe.id, c.id) in b_classe]
                    if not variables:
                        continue
                    compteur = modele.NewIntVar(0, len(variables),
                                                f"tardif_cl{classe.id}")
                    modele.Add(compteur == sum(variables))
                    compteurs.append(compteur)
                if compteurs:
                    pire = modele.NewIntVar(0, len(creneaux_tardifs), "pire_tardif")
                    modele.AddMaxEquality(pire, compteurs)
                    termes.append(p.equite_derniere_seance * pire)

        # ── S9 — équilibrage de la charge quotidienne des classes ──
        if p.equilibrage_charge_classes:
            for classe_id, charges in charges_classe.items():
                if len(charges) < 2:
                    continue
                plafond = self._classes[classe_id].max_heures_par_jour
                maxi = modele.NewIntVar(0, plafond, "")
                mini = modele.NewIntVar(0, plafond, "")
                modele.AddMaxEquality(maxi, charges)
                modele.AddMinEquality(mini, charges)
                termes.append(p.equilibrage_charge_classes * (maxi - mini))

        # ── S10 — demi-journées travaillées par les classes ───────
        if p.demi_journees_travaillees_classes:
            for demi_journees in demi_journees_classe.values():
                for travaillee in demi_journees:
                    termes.append(p.demi_journees_travaillees_classes * travaillee)

        if termes:
            modele.Minimize(sum(termes))

        duree_construction = time.perf_counter() - depart

        # ── Résolution ────────────────────────────────────────────
        depart_resolution = time.perf_counter()
        solveur = cp_model.CpSolver()
        solveur.parameters.max_time_in_seconds = float(self.options.limite_secondes)
        solveur.parameters.num_search_workers = self.options.nb_workers
        solveur.parameters.log_search_progress = False
        suivi = _SuiviRecherche(rappel, arret)
        statut = solveur.Solve(modele, suivi)
        duree_resolution = time.perf_counter() - depart_resolution
        interrompu = bool(arret and arret())

        resultat = Resultat(
            statut="INTERROMPU" if interrompu else solveur.StatusName(statut),
            duree_construction=duree_construction,
            duree_resolution=duree_resolution,
            nb_variables=len(y) + len(w),
            anomalies=anomalies,
        )

        if interrompu or statut not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return resultat

        resultat.valeur_objectif = int(solveur.ObjectiveValue()) if termes else None

        # Heures appartenant à une séance double, pour l'affichage.
        heures_doubles = set()
        for (cr_id, t1), d in d_vars.items():
            if solveur.Value(d):
                t2 = next(b for a, b in paires if a == t1)
                heures_doubles.add((cr_id, t1))
                heures_doubles.add((cr_id, t2))

        resultat.permanences = [
            cle for cle, var in permanences.items() if solveur.Value(var)
        ]

        index_cours = {cr.id: cr for cr in self.cours_requis}
        for (cr_id, creneau_id), var in y.items():
            if not solveur.Value(var):
                continue
            cr = index_cours[cr_id]
            possibles = salles_par_cours[cr_id]
            if len(possibles) == 1:
                salle_id = possibles[0]
            else:
                salle_id = next(
                    s for s in possibles
                    if solveur.Value(w[(cr_id, creneau_id, s)])
                )
            resultat.lecons.append(LeconPlanifiee(
                cours_requis_id=cr_id,
                classe_id=cr.classe_id,
                matiere_id=cr.matiere_id,
                professeur_id=cr.professeur_id,
                salle_id=salle_id,
                creneau_id=creneau_id,
                en_seance_double=(cr_id, creneau_id) in heures_doubles,
            ))

        return resultat
