"""
Jeu de données de démonstration.

Sert à découvrir la plateforme sans rien saisir : un collège réduit mais
complet, dont chaque élément illustre une notion du modèle — salle
spécialisée, indisponibilité d'un enseignant, séance double, professeur
bivalent. Assez petit pour être lu ligne à ligne, et assez contraint
pour que la génération ait un intérêt.

Quatre divisions de 4ᵉ année moyenne, 27 h de cours hebdomadaires,
7 enseignants, 7 salles.
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from ..models.class_ import Classe
from ..models.room import Salle
from ..models.schedule import EmploiDuTemps
from ..models.subject import Matiere
from ..models.task import TacheGeneration
from ..models.teacher import Professeur

NOM = "Collège de démonstration"
DESCRIPTION = (
    "Quatre divisions de 4ᵉ année moyenne, 27 h hebdomadaires chacune. "
    "Le jeu illustre les salles spécialisées (laboratoire, informatique, "
    "terrain), les enseignants bivalents, les indisponibilités et les "
    "séances doubles de deux heures."
)

# (nom, coefficient, type de salle requis, heures/semaine, séances doubles)
MATIERES = [
    ("Langue Arabe",        5.0, None,        5, 1),
    ("Mathématiques",       4.0, None,        5, 1),
    ("Langue Française",    3.0, None,        4, 1),
    ("Langue Anglaise",     2.0, None,        3, 0),
    ("Sciences Naturelles", 2.0, "labo",      2, 0),
    ("Sciences Physiques",  2.0, "labo",      2, 0),
    ("Histoire-Géographie", 2.0, None,        2, 0),
    ("Éducation Islamique", 2.0, None,        1, 0),
    ("Informatique",        1.0, "info",      1, 0),
    ("Éducation Physique",  1.0, "sport",     2, 1),
]

# (nom, capacité, type)
SALLES = [
    ("Salle 101", 36, "classique"),
    ("Salle 102", 36, "classique"),
    ("Salle 103", 36, "classique"),
    ("Salle 104", 36, "classique"),
    ("Laboratoire", 32, "labo"),
    ("Salle Informatique", 32, "info"),
    ("Terrain de sport", 60, "sport"),
]

CLASSES = [("4AM A", 32), ("4AM B", 32), ("4AM C", 31), ("4AM D", 30)]

# (nom, prénom, matières enseignées, indisponibilités)
# Les indisponibilités sont des (jour, heure de début) de la grille par
# défaut : c'est ainsi qu'elles sont stockées.
JEUDI_APRES_MIDI = [("Jeudi", "13:00"), ("Jeudi", "14:00"), ("Jeudi", "15:05")]
DIMANCHE_MATIN = [("Dimanche", "08:00"), ("Dimanche", "09:00")]

PROFESSEURS = [
    ("Benali",   "Karim",   ["Langue Arabe"],                             []),
    ("Meziane",  "Fatima",  ["Mathématiques"],                            []),
    ("Kaci",     "Leila",   ["Langue Française"],                         []),
    ("Rouag",    "Sofiane", ["Langue Anglaise"],            DIMANCHE_MATIN),
    # Enseignant bivalent : sciences naturelles et physiques.
    ("Hadj",     "Amina",   ["Sciences Naturelles", "Sciences Physiques"], []),
    ("Saadi",    "Nadia",   ["Histoire-Géographie", "Éducation Islamique"], []),
    # Partagé avec un autre établissement le jeudi après-midi.
    ("Cherif",   "Yasmine", ["Informatique", "Éducation Physique"], JEUDI_APRES_MIDI),
]


def deja_peuplee(db: Session, ecole_id: int) -> bool:
    """Vrai si l'établissement contient déjà des ressources."""
    for modele in (Matiere, Salle, Classe, Professeur):
        if db.query(modele).filter(modele.ecole_id == ecole_id).first():
            return True
    return False


def effacer(db: Session, ecole_id: int) -> None:
    """
    Vide les ressources de l'établissement.

    L'ordre suit les dépendances : les leçons et les tâches d'abord, puis
    les classes (qui référencent une salle attitrée), et les salles en
    dernier. La suppression passe par l'ORM pour que les cascades
    déclarées sur les relations s'appliquent.
    """
    from ..models.programme import LigneProgramme
    db.query(LigneProgramme).filter(
        LigneProgramme.ecole_id == ecole_id).delete()
    db.query(TacheGeneration).filter(
        TacheGeneration.ecole_id == ecole_id).delete()
    for edt in db.query(EmploiDuTemps).filter(
            EmploiDuTemps.ecole_id == ecole_id).all():
        db.delete(edt)
    db.flush()

    for modele in (Classe, Professeur, Matiere, Salle):
        for ligne in db.query(modele).filter(modele.ecole_id == ecole_id).all():
            db.delete(ligne)
    db.flush()


def charger(db: Session, ecole_id: int) -> Dict:
    """Crée le jeu de démonstration et retourne un récapitulatif."""
    from ..models.availability import DisponibiliteProfesseur

    matieres: Dict[str, Matiere] = {}
    for nom, coefficient, type_salle, _, _ in MATIERES:
        ligne = Matiere(ecole_id=ecole_id, nom=nom, coefficient=coefficient,
                        type_salle_requis=type_salle)
        db.add(ligne)
        matieres[nom] = ligne

    salles = []
    for nom, capacite, type_salle in SALLES:
        ligne = Salle(ecole_id=ecole_id, nom=nom, capacite=capacite,
                      type=type_salle)
        db.add(ligne)
        salles.append(ligne)
    db.flush()

    # Chaque division reçoit une salle ordinaire attitrée.
    ordinaires = [s for s in salles if s.type == "classique"]
    classes = []
    for rang, (nom, effectif) in enumerate(CLASSES):
        ligne = Classe(
            ecole_id=ecole_id, nom=nom, niveau="moyen", effectif=effectif,
            salle_attitree_id=ordinaires[rang % len(ordinaires)].id,
            max_heures_par_jour=7,
        )
        db.add(ligne)
        classes.append(ligne)

    professeurs = []
    for nom, prenom, enseigne, indisponibilites in PROFESSEURS:
        ligne = Professeur(
            ecole_id=ecole_id, nom=nom, prenom=prenom,
            max_heures_consecutives=4, max_heures_par_jour=6,
            max_heures_par_semaine=22, assure_permanences=True,
            matieres=[matieres[m] for m in enseigne],
        )
        db.add(ligne)
        db.flush()
        for jour, heure in indisponibilites:
            db.add(DisponibiliteProfesseur(
                professeur_id=ligne.id, jour=jour, heure_debut=heure,
                disponible=0))
        professeurs.append(ligne)

    # Le programme annuel est écrit lui aussi : le jeu doit être prêt à
    # générer, pas seulement à consulter.
    from ..models.programme import LigneProgramme
    par_nom = {m.nom: m for m in matieres.values()}
    titulaire = {}
    for prof in professeurs:
        for matiere in prof.matieres:
            titulaire.setdefault(matiere.nom, prof)
    for classe in classes:
        for nom, _, _, heures, doubles in MATIERES:
            db.add(LigneProgramme(
                ecole_id=ecole_id, classe_id=classe.id,
                matiere_id=par_nom[nom].id,
                professeur_id=titulaire[nom].id,
                heures_par_semaine=heures, nb_seances_doubles=doubles,
                max_heures_par_jour=2 if doubles else 1,
            ))

    edt = EmploiDuTemps(ecole_id=ecole_id, nom="Semaine type — démonstration",
                        annee_scolaire="2025-2026",
                        notes="Créé par le jeu de démonstration.")
    db.add(edt)
    db.commit()

    return {
        "nom": NOM,
        "emploi_du_temps_id": edt.id,
        "matieres": len(matieres),
        "salles": len(salles),
        "classes": len(classes),
        "professeurs": len(professeurs),
        "indisponibilites": sum(len(p[3]) for p in PROFESSEURS),
        "heures_par_classe": sum(h for _, _, _, h, _ in MATIERES),
        "lignes_programme": len(MATIERES) * len(classes),
        "lecons_a_placer": sum(h for _, _, _, h, _ in MATIERES) * len(classes),
    }


def programme(db: Session, ecole_id: int) -> List[Dict]:
    """
    Reconstitue les cours à planifier à partir des ressources en base.

    La recherche se fait par nom : le programme reste donc valable même
    si l'utilisateur a renommé ou complété quelques éléments, et signale
    clairement ce qui manque plutôt que de produire un programme muet.
    """
    par_nom_matiere = {
        m.nom: m for m in db.query(Matiere).filter(Matiere.ecole_id == ecole_id)}
    classes = db.query(Classe).filter(Classe.ecole_id == ecole_id).order_by(
        Classe.nom).all()
    enseignants = db.query(Professeur).filter(
        Professeur.ecole_id == ecole_id).all()

    manquantes = [nom for nom, *_ in MATIERES if nom not in par_nom_matiere]
    if manquantes or not classes:
        raise LookupError(
            "Le jeu de démonstration n'est pas chargé dans cet établissement"
            + (f" (matières absentes : {', '.join(manquantes)})" if manquantes
               else " (aucune classe)")
            + "."
        )

    # Premier enseignant qualifié pour chaque matière.
    titulaire: Dict[str, Professeur] = {}
    for nom in par_nom_matiere:
        for prof in enseignants:
            if any(m.nom == nom for m in prof.matieres):
                titulaire[nom] = prof
                break

    sans_enseignant = [nom for nom, *_ in MATIERES if nom not in titulaire]
    if sans_enseignant:
        raise LookupError(
            f"Aucun enseignant qualifié pour : {', '.join(sans_enseignant)}.")

    cours = []
    for classe in classes:
        for nom, _, _, heures, doubles in MATIERES:
            cours.append({
                "classe_id": classe.id,
                "matiere_id": par_nom_matiere[nom].id,
                "professeur_id": titulaire[nom].id,
                "heures_par_semaine": heures,
                "nb_seances_doubles": doubles,
                "max_heures_par_jour": 2 if doubles else 1,
            })
    return cours
