"""
Retouche manuelle d'un emploi du temps généré.

Le solveur produit une proposition ; le responsable garde le dernier
mot. Déplacer une leçon à la main doit donc être possible, mais sans
jamais produire une grille impossible — deux classes dans la même
salle, un enseignant à deux endroits à la fois.

D'où deux opérations :

  • `creneaux_possibles` balaie la grille et dit, pour chaque créneau,
    s'il accepte la leçon et sinon pourquoi. Trente-cinq créneaux à
    vérifier : la réponse est immédiate, ce qui permet à l'interface
    d'éclairer les cases pendant le glissement plutôt que de refuser
    après coup.

  • `deplacer` applique le mouvement après avoir revalidé. L'interface
    ne fait pas foi : deux responsables peuvent retoucher la même
    grille en même temps.

Le fouj se déplace d'un bloc. Deux leçons d'une même division au même
créneau sont ses deux demi-groupes : les séparer n'aurait aucun sens,
et laisserait la moitié de la classe sans cours.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models.availability import DisponibiliteProfesseur
from ..models.class_ import Classe
from ..models.programme import LigneProgramme
from ..models.room import Salle
from ..models.schedule import EmploiDuTemps, Lecon
from ..models.settings import FenetrePedagogique
from ..models.teacher import Professeur
from . import parametres

# Motifs de refus. Codes plutôt que phrases : l'interface les traduit,
# et l'arabe ne dépend pas d'une chaîne française renvoyée par l'API.
SEANCE_FERMEE = "seance_fermee"
PROFESSEUR_OCCUPE = "professeur_occupe"
PROFESSEUR_INDISPONIBLE = "professeur_indisponible"
DIVISION_OCCUPEE = "division_occupee"
AUCUNE_SALLE = "aucune_salle_libre"
FENETRE_PEDAGOGIQUE = "fenetre_pedagogique"
TROP_HEURES_PROFESSEUR = "plafond_journalier_professeur"
TROP_HEURES_DIVISION = "plafond_journalier_division"
TROP_CONSECUTIVES = "trop_heures_consecutives"
MATIERE_SATUREE = "plafond_journalier_matiere"


class _Contexte:
    """Tout ce qu'il faut pour juger un créneau, lu une seule fois."""

    def __init__(self, db: Session, ecole_id: int, edt: EmploiDuTemps):
        reglages = parametres.lire(db, ecole_id)
        self.jours: List[str] = list(reglages.grille.jours)
        self.horaires: List[Tuple[str, str]] = [
            (h[0], h[1]) for h in reglages.grille.horaires]
        self.index_seance = {h[0]: i for i, h in enumerate(self.horaires)}
        self.fermees = {(j, s) for j, seances in reglages.grille.fermetures
                        for s in seances}
        self.index_jour = {nom: i for i, nom in enumerate(self.jours)}

        self.lecons: List[Lecon] = list(edt.lecons)
        self.salles = {s.id: s for s in db.query(Salle).filter(
            Salle.ecole_id == ecole_id)}
        self.classes = {c.id: c for c in db.query(Classe).filter(
            Classe.ecole_id == ecole_id)}
        self.professeurs = {p.id: p for p in db.query(Professeur).filter(
            Professeur.ecole_id == ecole_id)}

        # Indisponibilités déclarées, par enseignant.
        self.indisponibilites = defaultdict(set)
        for ligne in db.query(DisponibiliteProfesseur).filter(
                DisponibiliteProfesseur.disponible == 0):
            self.indisponibilites[ligne.professeur_id].add(
                (ligne.jour, ligne.heure_debut))

        # Fenêtres pédagogiques : (matière, jour, séance) interdits.
        self.fenetres = set()
        for fenetre in db.query(FenetrePedagogique).filter(
                FenetrePedagogique.ecole_id == ecole_id):
            jour = (self.jours[fenetre.index_jour]
                    if fenetre.index_jour < len(self.jours) else None)
            if jour is None:
                continue
            for seance in (fenetre.seances_bloquees or []):
                self.fenetres.add((fenetre.matiere_id, jour, seance))

        # Plafond journalier d'une matière pour une division, tel que le
        # programme le déclare. Deux services d'une même matière (le
        # cours et le TD dédoublé) additionnent leurs plafonds : c'est
        # ce que la génération autorise, la retouche ne doit pas être
        # plus stricte qu'elle.
        self.plafond_matiere: Dict[Tuple[int, int], int] = defaultdict(int)
        for ligne in db.query(LigneProgramme).filter(
                LigneProgramme.ecole_id == ecole_id):
            self.plafond_matiere[(ligne.classe_id, ligne.matiere_id)] += \
                ligne.max_heures_par_jour

    def seance(self, lecon: Lecon) -> Optional[int]:
        return self.index_seance.get(lecon.heure_debut)


def _partenaires_fouj(contexte: _Contexte, lecon: Lecon) -> List[Lecon]:
    """
    Les leçons qui bougent avec celle-ci.

    Un fouj occupe la division une fois pour deux demi-groupes : les
    deux leçons partagent division, jour et heure.
    """
    return [autre for autre in contexte.lecons
            if autre.id != lecon.id
            and autre.classe_id == lecon.classe_id
            and autre.jour == lecon.jour
            and autre.heure_debut == lecon.heure_debut]


def _salle_pour(
    contexte: _Contexte,
    lecon: Lecon,
    jour: str,
    heure: str,
    deplacees: set,
    salles_prises: set,
) -> Optional[int]:
    """
    Salle utilisable à ce créneau : la même si elle est libre, sinon une
    autre du même type. Changer de salle est moins gênant que de
    refuser le déplacement.
    """
    occupees = {autre.salle_id for autre in contexte.lecons
                if autre.jour == jour and autre.heure_debut == heure
                and autre.id not in deplacees} | salles_prises

    actuelle = contexte.salles.get(lecon.salle_id)
    if lecon.salle_id not in occupees:
        return lecon.salle_id
    if actuelle is None:
        return None

    classe = contexte.classes.get(lecon.classe_id)
    # Un fouj ne reçoit qu'un demi-groupe : exiger l'effectif entier
    # écarterait des salles parfaitement utilisables.
    effectif = classe.effectif if classe else 0
    if _partenaires_fouj(contexte, lecon):
        effectif = (effectif + 1) // 2

    for salle in contexte.salles.values():
        if salle.id in occupees:
            continue
        if salle.type != actuelle.type:
            continue
        if salle.capacite < effectif:
            continue
        return salle.id
    return None


def _refus(
    contexte: _Contexte,
    groupe: List[Lecon],
    jour: str,
    heure: str,
) -> Tuple[Optional[str], Dict[int, int]]:
    """
    Motif de refus de ce créneau, ou None s'il convient.

    Rend aussi la salle retenue pour chaque leçon du groupe.
    """
    seance = contexte.index_seance.get(heure)
    if seance is None:
        return SEANCE_FERMEE, {}
    if (contexte.index_jour.get(jour, -1), seance) in contexte.fermees:
        return SEANCE_FERMEE, {}

    deplacees = {lecon.id for lecon in groupe}
    reference = groupe[0]

    # La division n'a pas déjà cours ailleurs à ce créneau.
    for autre in contexte.lecons:
        if autre.id in deplacees:
            continue
        if (autre.classe_id == reference.classe_id
                and autre.jour == jour and autre.heure_debut == heure):
            return DIVISION_OCCUPEE, {}

    for lecon in groupe:
        # L'enseignant n'est pas déjà en cours.
        for autre in contexte.lecons:
            if autre.id in deplacees:
                continue
            if (autre.professeur_id == lecon.professeur_id
                    and autre.jour == jour and autre.heure_debut == heure):
                return PROFESSEUR_OCCUPE, {}

        if (jour, heure) in contexte.indisponibilites.get(
                lecon.professeur_id, ()):
            return PROFESSEUR_INDISPONIBLE, {}

        if (lecon.matiere_id, jour, seance) in contexte.fenetres:
            return FENETRE_PEDAGOGIQUE, {}

    # Plafonds journaliers, calculés sur la journée d'arrivée.
    du_jour = [autre for autre in contexte.lecons
               if autre.jour == jour and autre.id not in deplacees]

    heures_division = len({autre.heure_debut for autre in du_jour
                           if autre.classe_id == reference.classe_id})
    classe = contexte.classes.get(reference.classe_id)
    if classe and heures_division + 1 > classe.max_heures_par_jour:
        return TROP_HEURES_DIVISION, {}

    for lecon in groupe:
        professeur = contexte.professeurs.get(lecon.professeur_id)
        heures_prof = len([autre for autre in du_jour
                           if autre.professeur_id == lecon.professeur_id])
        if professeur and heures_prof + 1 > professeur.max_heures_par_jour:
            return TROP_HEURES_PROFESSEUR, {}

        if professeur and professeur.max_heures_consecutives:
            positions = sorted(
                {contexte.index_seance[autre.heure_debut]
                 for autre in du_jour
                 if autre.professeur_id == lecon.professeur_id
                 and autre.heure_debut in contexte.index_seance} | {seance})
            suite = 1
            plus_longue = 1
            for precedent, courant in zip(positions, positions[1:]):
                suite = suite + 1 if courant == precedent + 1 else 1
                plus_longue = max(plus_longue, suite)
            if plus_longue > professeur.max_heures_consecutives:
                return TROP_CONSECUTIVES, {}

        plafond = contexte.plafond_matiere.get(
            (lecon.classe_id, lecon.matiere_id))
        if plafond:
            deja = len({autre.heure_debut for autre in du_jour
                        if autre.classe_id == lecon.classe_id
                        and autre.matiere_id == lecon.matiere_id})
            if deja + 1 > plafond:
                return MATIERE_SATUREE, {}

    # Salles : attribuées une par une pour que les deux demi-groupes
    # d'un fouj n'héritent pas de la même.
    salles = {}
    prises = set()
    for lecon in groupe:
        salle_id = _salle_pour(contexte, lecon, jour, heure, deplacees, prises)
        if salle_id is None:
            return AUCUNE_SALLE, {}
        salles[lecon.id] = salle_id
        prises.add(salle_id)

    return None, salles


def creneaux_possibles(db: Session, ecole_id: int, edt: EmploiDuTemps,
                       lecon_id: int) -> Dict:
    """Grille complète, annotée créneau par créneau."""
    contexte = _Contexte(db, ecole_id, edt)
    lecon = next((l for l in contexte.lecons if l.id == lecon_id), None)
    if lecon is None:
        raise ValueError("Leçon introuvable dans cet emploi du temps.")

    groupe = [lecon] + _partenaires_fouj(contexte, lecon)
    creneaux = []
    for jour in contexte.jours:
        for debut, fin in contexte.horaires:
            actuel = jour == lecon.jour and debut == lecon.heure_debut
            motif, salles = (None, {}) if actuel else _refus(
                contexte, groupe, jour, debut)
            creneaux.append({
                "jour": jour,
                "heure_debut": debut,
                "heure_fin": fin,
                "actuel": actuel,
                "possible": motif is None,
                "motif": motif,
                "salles": {str(cle): valeur for cle, valeur in salles.items()},
            })

    return {
        "lecon_id": lecon.id,
        "classe_id": lecon.classe_id,
        "professeur_id": lecon.professeur_id,
        "matiere_id": lecon.matiere_id,
        "groupe": [l.id for l in groupe],
        "creneaux": creneaux,
    }


def deplacer(db: Session, ecole_id: int, edt: EmploiDuTemps, lecon_id: int,
             jour: str, heure_debut: str) -> Dict:
    """
    Pose la leçon — et son partenaire de fouj — sur un autre créneau.

    Revalidé côté serveur : l'interface a pu être calculée sur un état
    déjà périmé par la retouche d'un collègue.
    """
    contexte = _Contexte(db, ecole_id, edt)
    lecon = next((l for l in contexte.lecons if l.id == lecon_id), None)
    if lecon is None:
        raise ValueError("Leçon introuvable dans cet emploi du temps.")

    seance = contexte.index_seance.get(heure_debut)
    if jour not in contexte.index_jour or seance is None:
        raise ValueError("Ce créneau n'existe pas dans la grille horaire.")

    groupe = [lecon] + _partenaires_fouj(contexte, lecon)
    if jour == lecon.jour and heure_debut == lecon.heure_debut:
        return {"deplacees": [], "motif": None}

    motif, salles = _refus(contexte, groupe, jour, heure_debut)
    if motif is not None:
        return {"deplacees": [], "motif": motif}

    _, fin = contexte.horaires[seance]
    for membre in groupe:
        membre.jour = jour
        membre.heure_debut = heure_debut
        membre.heure_fin = fin
        membre.salle_id = salles[membre.id]
    db.commit()
    return {"deplacees": [membre.id for membre in groupe], "motif": None}
