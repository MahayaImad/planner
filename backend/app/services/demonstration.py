"""
Jeu de données de démonstration : le CEM à 20 divisions.

Installe l'établissement réel de bout en bout — parc de salles, corps
enseignant avec ses plafonds de service, programme annuel complet avec
ses fouj, journées d'inspection et fermeture du mardi après-midi. Rien
n'est simplifié : c'est le cas qui a servi à régler le solveur, et il
sert ici à découvrir la plateforme sans rien saisir.

Le jeu est décrit une seule fois, dans donnees/cem20.py, et partagé
avec les tests : un exemple qui diverge de ce qu'on vérifie ne
prouverait rien.
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from donnees import cem20

from ..models.availability import DisponibiliteProfesseur
from ..models.class_ import Classe
from ..models.programme import LigneProgramme
from ..models.room import Salle
from ..models.schedule import EmploiDuTemps
from ..models.settings import FenetrePedagogique, ParametresEtablissement
from ..models.subject import Matiere
from ..models.task import TacheGeneration
from ..models.teacher import Professeur

NOM = "CEM Ibn Khaldoun — 20 divisions"
DESCRIPTION = (
    "L'établissement complet : 20 divisions de la 1ʳᵉ à la 4ᵉ année "
    "moyenne, 39 enseignants, 32 salles. Programme officiel avec ses "
    "dédoublements en demi-groupes, journées d'inspection, mardi "
    "après-midi fermé et plafonds de service hebdomadaire."
)


def _heures_par_classe() -> int:
    """Volume hebdomadaire d'une division ; un fouj n'y compte qu'une fois."""
    vus, total = set(), 0
    premiere = cem20.classes[0].id
    for cr in cem20.cours_requis:
        if cr.classe_id != premiere:
            continue
        if cr.couplage_id:
            if cr.couplage_id in vus:
                continue
            vus.add(cr.couplage_id)
        total += cr.heures_par_semaine
    return total


def resume() -> Dict:
    """Décrit le jeu sans rien créer."""
    return {
        "nom": NOM,
        "description": DESCRIPTION,
        "matieres": len(cem20.matieres),
        "salles": len(cem20.salles),
        "classes": len(cem20.classes),
        "professeurs": len(cem20.professeurs),
        "heures_par_classe": _heures_par_classe(),
        "lignes_programme": len(cem20.cours_requis),
        "lecons_a_placer": sum(c.heures_par_semaine for c in cem20.cours_requis),
        "fenetres_pedagogiques": len(cem20.fenetres_pedagogiques),
    }


def deja_peuplee(db: Session, ecole_id: int) -> bool:
    """Vrai si l'établissement contient déjà des ressources."""
    for modele in (Matiere, Salle, Classe, Professeur):
        if db.query(modele).filter(modele.ecole_id == ecole_id).first():
            return True
    return False


def effacer(db: Session, ecole_id: int) -> None:
    """
    Vide les ressources de l'établissement.

    L'ordre suit les dépendances : programme, tâches et leçons d'abord,
    puis les classes — qui référencent une salle attitrée — et les
    salles en dernier. La suppression passe par l'ORM là où des
    cascades sont déclarées sur les relations.
    """
    for modele in (LigneProgramme, FenetrePedagogique, TacheGeneration):
        db.query(modele).filter(modele.ecole_id == ecole_id).delete()
    for edt in db.query(EmploiDuTemps).filter(
            EmploiDuTemps.ecole_id == ecole_id).all():
        db.delete(edt)
    db.flush()

    for modele in (Classe, Professeur, Matiere, Salle):
        for ligne in db.query(modele).filter(modele.ecole_id == ecole_id).all():
            db.delete(ligne)
    db.flush()


def charger(db: Session, ecole_id: int) -> Dict:
    """Installe le jeu complet et retourne un récapitulatif."""
    # ── Matières, avec le type de salle qu'elles exigent ──────────
    type_salle_de: Dict[int, str] = {}
    for niveau in cem20.PROGRAMME.values():
        for code, ligne in niveau.items():
            type_salle_de.setdefault(cem20.ID_MATIERE[code],
                                     ligne["Required_Room_Type"])

    id_matiere: Dict[int, int] = {}
    for matiere in cem20.matieres:
        type_requis = type_salle_de.get(matiere.id)
        ligne = Matiere(
            ecole_id=ecole_id, nom=matiere.nom, coefficient=matiere.coefficient,
            # Le type ordinaire n'est pas une exigence : les cours qui le
            # portent restent dans la salle attitrée de la division.
            type_salle_requis=(None if type_requis == cem20.TYPE_SALLE_ORDINAIRE
                               else type_requis),
        )
        db.add(ligne)
        db.flush()
        id_matiere[matiere.id] = ligne.id

    # ── Salles ────────────────────────────────────────────────────
    id_salle: Dict[int, int] = {}
    for salle in cem20.salles:
        ligne = Salle(ecole_id=ecole_id, nom=salle.nom, capacite=salle.capacite,
                      type=salle.type)
        db.add(ligne)
        db.flush()
        id_salle[salle.id] = ligne.id

    # ── Divisions, chacune dans sa salle attitrée ─────────────────
    id_classe: Dict[int, int] = {}
    for classe in cem20.classes:
        ligne = Classe(
            ecole_id=ecole_id, nom=classe.nom, niveau=classe.niveau,
            effectif=classe.effectif,
            salle_attitree_id=id_salle.get(classe.salle_attitree_id),
            max_heures_par_jour=classe.max_heures_par_jour,
        )
        db.add(ligne)
        db.flush()
        id_classe[classe.id] = ligne.id

    # ── Enseignants et leurs indisponibilités ─────────────────────
    creneaux = {c.id: c for c in cem20.creneaux}
    id_prof: Dict[int, int] = {}
    nb_indisponibilites = 0
    for prof in cem20.professeurs:
        ligne = Professeur(
            ecole_id=ecole_id, nom=prof.nom, prenom=prof.prenom,
            max_heures_consecutives=prof.max_heures_consecutives,
            max_heures_par_jour=prof.max_heures_par_jour,
            max_heures_par_semaine=prof.max_heures_par_semaine,
            assure_permanences=prof.assure_permanences,
            matieres=[db.get(Matiere, id_matiere[m]) for m in prof.matieres_ids],
        )
        db.add(ligne)
        db.flush()
        id_prof[prof.id] = ligne.id

        # creneaux_disponibles vide signifie « disponible partout » :
        # seuls les créneaux réellement retirés donnent une ligne.
        if prof.creneaux_disponibles:
            for creneau in cem20.creneaux:
                if creneau.id not in prof.creneaux_disponibles:
                    db.add(DisponibiliteProfesseur(
                        professeur_id=ligne.id, jour=creneau.jour,
                        heure_debut=creneau.heure_debut, disponible=0))
                    nb_indisponibilites += 1

    # ── Programme annuel, fouj compris ────────────────────────────
    for cr in cem20.cours_requis:
        db.add(LigneProgramme(
            ecole_id=ecole_id,
            classe_id=id_classe[cr.classe_id],
            matiere_id=id_matiere[cr.matiere_id],
            professeur_id=id_prof[cr.professeur_id],
            heures_par_semaine=cr.heures_par_semaine,
            nb_seances_doubles=cr.nb_seances_doubles,
            max_heures_par_jour=cr.max_heures_par_jour,
            couplage_id=cr.couplage_id,
            groupe=cr.groupe,
        ))

    # ── Journées d'inspection ─────────────────────────────────────
    for fenetre in cem20.fenetres_pedagogiques:
        db.add(FenetrePedagogique(
            ecole_id=ecole_id,
            matiere_id=id_matiere[fenetre.matiere_id],
            index_jour=fenetre.index_jour,
            seances_bloquees=";".join(str(s) for s in sorted(fenetre.seances_bloquees)),
            libelle=fenetre.libelle,
        ))

    # ── Réglages : grille, fermetures et pondérations ─────────────
    reglages = db.query(ParametresEtablissement).filter(
        ParametresEtablissement.ecole_id == ecole_id).first()
    if reglages is None:
        reglages = ParametresEtablissement(ecole_id=ecole_id)
        db.add(reglages)
    reglages.grille = {
        "jours": list(cem20.JOURS),
        "horaires": [list(h) for h in cem20.HORAIRES],
        "shifts": [[nom, list(seances)] for nom, seances in cem20.SHIFTS],
        "fermetures": [[jour, list(seances)] for jour, seances in cem20.FERMETURES],
    }
    # Les seuils sont indexés par des entiers ; JSON n'a que des clés
    # texte, et les relire sans conversion donnerait deux formes pour la
    # même donnée selon qu'elle sort du code ou de la base.
    poids = {cle: ({str(k): v for k, v in valeur.items()}
                   if isinstance(valeur, dict) else valeur)
             for cle, valeur in vars(cem20.ponderations).items()}
    reglages.ponderations = poids
    reglages.presence_minimale = dict(cem20.options.presence_minimale)
    reglages.type_salle_ordinaire = cem20.options.type_salle_ordinaire
    reglages.limite_secondes = 300

    edt = EmploiDuTemps(ecole_id=ecole_id, nom="Semaine type 2025-2026",
                        annee_scolaire="2025-2026",
                        notes="Créé par le jeu de démonstration.")
    db.add(edt)
    db.commit()

    return {**resume(), "emploi_du_temps_id": edt.id,
            "indisponibilites": nb_indisponibilites}
