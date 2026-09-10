"""
Modèles de données du générateur d'emplois du temps.

Le vocabulaire suit celui d'un établissement algérien (CEM / lycée) :
la semaine est découpée en JOURS, chaque jour en deux DEMI-JOURNÉES
(matin / après-midi) séparées par la pause déjeuner, et chaque
demi-journée en SÉANCES.

La distinction demi-journée est structurante : une « heure de trou »
n'a de sens qu'à l'intérieur d'une demi-journée — la coupure du
déjeuner n'est pas un trou, et deux séances de part et d'autre du
déjeuner ne sont pas consécutives.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

MATIN = "matin"
APRES_MIDI = "apres-midi"

# Semaine scolaire algérienne : le week-end est vendredi-samedi.
JOURS_SEMAINE_DZ = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]


# ══════════════════════════════════════════════════════════════════
#  Grille horaire
# ══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Creneau:
    """
    Une séance dans la semaine (ex : Lundi, 2ᵉ séance du matin).

    Deux numérotations coexistent, et la distinction compte :
      index_seance        position OFFICIELLE dans la journée (0..6). C'est
                          celle des règles de l'établissement — « séance 7 »,
                          fermetures, fenêtres pédagogiques.
      index_demi_journee  position parmi les séances OUVERTES de la
                          demi-journée. C'est celle qui sert à détecter les
                          trous : une séance fermée n'est pas un trou.
    """
    id: int
    jour: str
    index_jour: int          # 0 = premier jour travaillé de la semaine
    demi_journee: str        # MATIN | APRES_MIDI
    index_seance: int        # 0-based, numérotation officielle dans la journée
    index_demi_journee: int  # 0-based, parmi les séances ouvertes de la demi-journée
    index_dans_jour: int     # 0-based, parmi les séances ouvertes de la journée
    heure_debut: str         # "08:00"
    heure_fin: str           # "08:55"

    @property
    def cle_demi_journee(self) -> Tuple[str, str]:
        return (self.jour, self.demi_journee)

    def __repr__(self):
        return f"{self.jour} {self.heure_debut}-{self.heure_fin}"


@dataclass
class GrilleHoraire:
    """
    Grille horaire d'un établissement : quels jours, quelles séances.

    Entièrement paramétrable — c'est ce qui permet à chaque CEM
    d'encoder ses propres horaires plutôt que de subir un calendrier
    codé en dur.
    """
    jours: List[str]
    seances_matin: List[Tuple[str, str]]
    seances_apres_midi: List[Tuple[str, str]]
    creneaux: List[Creneau] = field(default_factory=list)

    # ── Construction ──────────────────────────────────────────────
    @classmethod
    def depuis_configuration(
        cls,
        jours: Sequence[str],
        horaires: Sequence[Tuple[str, str]],
        shifts: Sequence[Tuple[str, Sequence[int]]],
        fermetures: Sequence[Tuple[int, Sequence[int]]] = (),
    ) -> "GrilleHoraire":
        """
        Construit une grille à partir de la configuration d'un
        établissement.

        horaires    : horaire de chaque séance de la journée, indexé de 0
                      à slots_per_day-1.
        shifts      : demi-journées, sous la forme (nom, [index de séances]).
        fermetures  : (index du jour, [index de séances]) fermées — par
                      exemple le mardi après-midi. Les séances fermées ne
                      donnent lieu à aucun créneau : elles ne peuvent donc
                      ni être remplies, ni compter comme un trou.
        """
        fermees = {(j, s) for j, seances in fermetures for s in seances}
        shift_de_seance = {s: nom for nom, seances in shifts for s in seances}

        grille = cls(jours=list(jours), seances_matin=[], seances_apres_midi=[])
        cid = 1
        for index_jour, jour in enumerate(jours):
            index_dans_jour = 0
            compteur_shift: Dict[str, int] = {}
            for index_seance, (debut, fin) in enumerate(horaires):
                if (index_jour, index_seance) in fermees:
                    continue
                nom_shift = shift_de_seance.get(index_seance, MATIN)
                position = compteur_shift.get(nom_shift, 0)
                compteur_shift[nom_shift] = position + 1
                grille.creneaux.append(Creneau(
                    id=cid, jour=jour, index_jour=index_jour,
                    demi_journee=nom_shift, index_seance=index_seance,
                    index_demi_journee=position, index_dans_jour=index_dans_jour,
                    heure_debut=debut, heure_fin=fin,
                ))
                cid += 1
                index_dans_jour += 1

        grille.seances_matin = sorted(
            {(c.heure_debut, c.heure_fin) for c in grille.creneaux if c.demi_journee == MATIN})
        grille.seances_apres_midi = sorted(
            {(c.heure_debut, c.heure_fin) for c in grille.creneaux if c.demi_journee == APRES_MIDI})
        return grille

    @classmethod
    def construire(
        cls,
        jours: Sequence[str] = tuple(JOURS_SEMAINE_DZ),
        seances_matin: Sequence[Tuple[str, str]] = (
            ("08:00", "08:55"), ("09:00", "09:55"),
            ("10:05", "11:00"), ("11:05", "12:00"),
        ),
        seances_apres_midi: Sequence[Tuple[str, str]] = (
            ("13:00", "13:55"), ("14:00", "14:55"), ("15:05", "16:00"),
        ),
        fermetures: Sequence[Tuple[int, Sequence[int]]] = (),
    ) -> "GrilleHoraire":
        """Grille classique matin / après-midi."""
        horaires = list(seances_matin) + list(seances_apres_midi)
        shifts = [
            (MATIN, list(range(len(seances_matin)))),
            (APRES_MIDI, list(range(len(seances_matin), len(horaires)))),
        ]
        return cls.depuis_configuration(jours, horaires, shifts, fermetures)

    @classmethod
    def depuis_creneaux(cls, creneaux: Sequence["Creneau"]) -> "GrilleHoraire":
        """
        Reconstruit une grille à partir d'une liste de créneaux bruts
        (compatibilité : créneaux sans index, produits par l'API).
        La demi-journée est déduite de l'heure de début.
        """
        if creneaux and isinstance(creneaux[0], Creneau):
            jours, vus = [], set()
            for c in creneaux:
                if c.jour not in vus:
                    vus.add(c.jour)
                    jours.append(c.jour)
            matin = sorted({(c.heure_debut, c.heure_fin) for c in creneaux if c.demi_journee == MATIN})
            pm = sorted({(c.heure_debut, c.heure_fin) for c in creneaux if c.demi_journee == APRES_MIDI})
            return cls(jours=jours, seances_matin=matin, seances_apres_midi=pm,
                       creneaux=list(creneaux))
        raise ValueError("Créneaux incompatibles : utilisez GrilleHoraire.construire().")

    # ── Index dérivés ─────────────────────────────────────────────
    def index(self) -> Dict[int, Creneau]:
        return {c.id: c for c in self.creneaux}

    def par_jour(self) -> Dict[str, List[Creneau]]:
        groupes: Dict[str, List[Creneau]] = {}
        for c in self.creneaux:
            groupes.setdefault(c.jour, []).append(c)
        for v in groupes.values():
            v.sort(key=lambda c: c.index_dans_jour)
        return groupes

    def par_demi_journee(self) -> Dict[Tuple[str, str], List[Creneau]]:
        groupes: Dict[Tuple[str, str], List[Creneau]] = {}
        for c in self.creneaux:
            groupes.setdefault(c.cle_demi_journee, []).append(c)
        for v in groupes.values():
            v.sort(key=lambda c: c.index_demi_journee)
        return groupes

    def paires_consecutives(self) -> List[Tuple[int, int]]:
        """
        Couples (t, t_suivant) réellement adjacents, c'est-à-dire dans
        la même demi-journée. Base des séances doubles.
        """
        paires = []
        for creneaux_dj in self.par_demi_journee().values():
            for a, b in zip(creneaux_dj, creneaux_dj[1:]):
                if b.index_seance == a.index_seance + 1:
                    paires.append((a.id, b.id))
        return paires

    @property
    def creneaux_matin(self) -> Set[int]:
        return {c.id for c in self.creneaux if c.demi_journee == MATIN}

    def __len__(self):
        return len(self.creneaux)


# ══════════════════════════════════════════════════════════════════
#  Ressources de l'établissement
# ══════════════════════════════════════════════════════════════════

@dataclass
class Salle:
    id: int
    nom: str
    capacite: int = 40
    type: str = "classique"  # classique | labo | info | sport


@dataclass
class Matiere:
    id: int
    nom: str
    coefficient: float = 1.0
    type_salle_requis: Optional[str] = None
    # Matière « lourde » : à placer de préférence le matin.
    prefere_matin: bool = False


@dataclass
class Professeur:
    id: int
    nom: str
    prenom: str
    matieres_ids: List[int] = field(default_factory=list)
    # Créneaux où le prof peut enseigner. Vide = disponible partout.
    creneaux_disponibles: Set[int] = field(default_factory=set)
    max_heures_consecutives: int = 4
    max_heures_par_jour: int = 6
    # Service hebdomadaire maximum (None = pas de plafond).
    max_heures_par_semaine: Optional[int] = None
    # Regrouper le service sur au plus N jours (None = pas de limite).
    max_jours_presence: Optional[int] = None
    # L'enseignant peut-il assurer une permanence dans ses heures creuses ?
    assure_permanences: bool = True

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}"

    def est_disponible(self, creneau_id: int) -> bool:
        return not self.creneaux_disponibles or creneau_id in self.creneaux_disponibles


@dataclass
class Classe:
    id: int
    nom: str
    niveau: str = "moyen"
    effectif: int = 34
    # Salle de classe attitrée : les élèves ne bougent que pour
    # labo / informatique / sport.
    salle_attitree_id: Optional[int] = None
    max_heures_par_jour: int = 6
    # Nombre maximum de demi-journées travaillées (None = pas de limite).
    max_demi_journees: Optional[int] = None


@dataclass
class CoursRequis:
    """
    Exigence pédagogique : la classe X suit N heures/semaine de la
    matière Y avec le professeur Z.
    """
    id: int
    classe_id: int
    matiere_id: int
    professeur_id: int
    heures_par_semaine: int
    type_salle_requis: Optional[str] = None   # surcharge celui de la matière
    # Nombre de séances de 2 h consécutives à réserver dans le volume.
    nb_seances_doubles: int = 0
    # Plafond d'heures de cette matière dans une même journée.
    max_heures_par_jour: int = 2
    # Effectif réel (demi-groupe de TP → moitié de la classe).
    effectif: Optional[int] = None
    # ── Fouj : dédoublement en demi-groupes ───────────────────────
    # Deux cours portant le même couplage_id sont donnés EN MÊME TEMPS
    # à deux demi-groupes de la même classe, par deux enseignants et
    # dans deux salles distinctes (ex. TD arabe / TD maths, ou TP
    # physique / TP sciences). La classe n'est occupée qu'une fois.
    couplage_id: Optional[str] = None
    groupe: str = ""          # "" = classe entière, sinon "G1" / "G2"
    # Séances où cette matière est interdite (inspection, coordination).
    creneaux_interdits: Set[int] = field(default_factory=set)


@dataclass
class FenetrePedagogique:
    """
    Fenêtre où une matière est interdite dans tout l'établissement.

    Sert aux journées d'inspection et aux réunions de coordination :
    « aucun cours d'arabe le lundi matin » libère l'ensemble des
    professeurs d'arabe à ce moment-là.
    """
    matiere_id: int
    index_jour: int
    seances_bloquees: Set[int]      # numéros OFFICIELS de séance
    libelle: str = ""


@dataclass
class LeconPlanifiee:
    """Résultat : une heure de cours placée dans la semaine."""
    cours_requis_id: int
    classe_id: int
    matiere_id: int
    professeur_id: int
    salle_id: int
    creneau_id: int
    # Vraie si cette heure appartient à une séance double.
    en_seance_double: bool = False


# ══════════════════════════════════════════════════════════════════
#  Paramétrage du solveur
# ══════════════════════════════════════════════════════════════════

@dataclass
class Options:
    """Contraintes DURES activables (règles non négociables)."""
    zero_trou_classes: bool = True
    salle_attitree: bool = True
    # Nom du type de salle ordinaire dans le parc de l'établissement.
    # Tout autre type est spécialisé (labo, informatique, stade) et
    # n'est mobilisé que par les matières qui l'exigent.
    type_salle_ordinaire: str = "classique"
    reserver_salles_specialisees: bool = True
    verifier_competence_professeur: bool = True
    verifier_capacite_salle: bool = True
    # Deux heures d'une matière le même jour doivent être accolées.
    grouper_matiere_meme_jour: bool = True
    # Présence minimale d'une classe par demi-journée : {nom_shift: heures}.
    # Évite qu'une classe ne vienne que pour une heure le matin.
    presence_minimale: Dict[str, int] = field(default_factory=dict)
    # Portée de la pénalité « heure isolée » d'un professeur.
    mode_heure_isolee: str = "PER_SHIFT"     # PER_SHIFT | PER_DAY | AUCUN
    # Heures de permanence qu'un professeur peut assurer dans ses trous.
    permanences_max_par_prof: int = 2
    limite_secondes: int = 60
    nb_workers: int = 8


@dataclass
class Ponderations:
    """
    Poids des contraintes SOUPLES (souhaits). Mettre 0 pour désactiver
    un critère. Ce sont ces poids que le responsable arbitre.
    """
    # ── Service des professeurs ───────────────────────────────────
    # Coût d'une heure creuse isolée dans la journée d'un professeur.
    trous_professeurs: int = 6
    # Surcoût d'un trou de deux heures d'affilée : un vide de 2 h est
    # bien pire que deux trous d'une heure situés à des jours différents.
    trous_doubles_professeurs: int = 25
    # Journée hachée : plus d'une heure creuse dans la même journée,
    # qu'elles se suivent ou non (occupé, libre, occupé, libre…).
    # L'enseignant reste sur place du matin au soir sans jamais
    # disposer d'un vrai temps libre. Compté par heure creuse au-delà
    # de la PREMIÈRE de la journée, les deux demi-journées confondues,
    # et pesé au-dessus du vide de deux heures.
    #
    # Mesuré sur un CEM de 20 divisions : sans ce poids, 11 journées
    # d'enseignant comptent plus d'une heure creuse ; à 40 il en reste
    # une, à 80 aucune.
    journee_hachee_professeur: int = 80
    # Professeur qui ne vient assurer qu'une seule heure sur la
    # demi-journée : déplacement disproportionné.
    heure_isolee_professeur: int = 12
    # Chaque jour de présence en moins est un jour libéré.
    jours_presence_professeurs: int = 3
    # Charge quotidienne : atteindre N heures de cours dans la journée
    # coûte ce poids, EN PLUS de ceux des seuils inférieurs. Une journée
    # de 6 h paie donc le seuil 5 et le seuil 6 : la fatigue ne croît
    # pas linéairement, les dernières heures pèsent plus lourd.
    penalites_heures_par_jour: Dict[int, int] = field(
        default_factory=lambda: {5: 15, 6: 45})
    # Bonus quand un trou est comblé par une heure de permanence
    # (accueil, étude surveillée) : le professeur est présent utilement.
    recompense_permanence: int = 4

    # ── Journée des élèves ────────────────────────────────────────
    # Coût d'OCCUPATION de chaque séance de la journée, indexée à partir
    # de 0. La séance nommée « slot_N » par l'établissement porte donc
    # l'index N-1 :
    #
    #   index 0  (slot 1, 08:00) démarrage matinal, à éviter
    #   index 3  (slot 4, 11:05) prolonge la matinée jusqu'à midi
    #   index 4  (slot 5, 13:00) reprise immédiate après le déjeuner
    #   index 5  (slot 6, 14:00) après-midi qui s'étire
    #   index 6  (slot 7, 15:05) dernière séance, la plus pénalisée
    #
    # Les séances 2 et 3 (09:00 et 10:05) ne coûtent rien : c'est le
    # cœur de matinée, le moment le plus favorable aux apprentissages.
    penalites_seance: Dict[int, int] = field(
        default_factory=lambda: {0: 20, 3: 8, 4: 10, 5: 30, 6: 150})
    # Répartir équitablement les dernières séances entre les classes :
    # aucune division ne doit hériter de toutes les fins tardives.
    equite_derniere_seance: int = 25
    seance_soumise_a_equite: int = 6
    equilibrage_charge_classes: int = 4
    demi_journees_travaillees_classes: int = 0
    matieres_lourdes_apres_midi: int = 0

    def est_neutre(self) -> bool:
        return all(
            not v for k, v in vars(self).items() if k != "seance_soumise_a_equite"
        )


@dataclass
class Resultat:
    statut: str                       # OPTIMAL | FEASIBLE | INFEASIBLE | UNKNOWN
    lecons: List[LeconPlanifiee] = field(default_factory=list)
    duree_construction: float = 0.0
    duree_resolution: float = 0.0
    valeur_objectif: Optional[int] = None
    nb_variables: int = 0
    # Diagnostics remontés avant la résolution.
    anomalies: List[Tuple[str, str]] = field(default_factory=list)
    # Heures de permanence attribuées : (professeur_id, creneau_id).
    permanences: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def reussi(self) -> bool:
        return self.statut in ("OPTIMAL", "FEASIBLE")
