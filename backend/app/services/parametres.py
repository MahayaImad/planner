"""
Lecture et écriture des réglages de planification.

Un établissement qui n'a jamais rien réglé doit pouvoir générer tout de
suite : la lecture retourne alors les valeurs par défaut sans rien
créer en base.
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from ..models.settings import (
    GRILLE_DEFAUT, PONDERATIONS_DEFAUT, FenetrePedagogique,
    ParametresEtablissement,
)
from ..schemas.settings import (
    FenetreRead, GrilleInput, ParametresRead, ParametresUpdate, PonderationsInput,
)


def _entites(db: Session, ecole_id: int) -> ParametresEtablissement:
    ligne = db.query(ParametresEtablissement).filter(
        ParametresEtablissement.ecole_id == ecole_id).first()
    if ligne is None:
        ligne = ParametresEtablissement(
            ecole_id=ecole_id,
            grille=dict(GRILLE_DEFAUT),
            ponderations=dict(PONDERATIONS_DEFAUT),
            presence_minimale={},
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
    return ligne


def lire(db: Session, ecole_id: int) -> ParametresRead:
    ligne = _entites(db, ecole_id)
    return ParametresRead(
        grille=GrilleInput(**ligne.grille),
        # Les clés d'un objet JSON sont des chaînes : les pénalités par
        # séance reviennent donc indexées par « "0" » plutôt que 0.
        ponderations=PonderationsInput(**ligne.ponderations),
        presence_minimale=ligne.presence_minimale or {},
        type_salle_ordinaire=ligne.type_salle_ordinaire,
        limite_secondes=ligne.limite_secondes,
    )


def valider_grille(grille: GrilleInput) -> None:
    """Refuse une grille qui rendrait toute génération impossible."""
    if not grille.jours:
        raise ValueError("La grille doit comporter au moins un jour travaillé.")
    if not grille.horaires:
        raise ValueError("La grille doit comporter au moins une séance.")

    nb_seances = len(grille.horaires)
    couvertes = set()
    for nom, seances in grille.shifts:
        for s in seances:
            if not 0 <= s < nb_seances:
                raise ValueError(
                    f"La demi-journée « {nom} » référence la séance {s + 1}, "
                    f"or la journée n'en compte que {nb_seances}.")
            if s in couvertes:
                raise ValueError(
                    f"La séance {s + 1} appartient à deux demi-journées.")
            couvertes.add(s)
    manquantes = set(range(nb_seances)) - couvertes
    if manquantes:
        raise ValueError(
            "Séances qui n'appartiennent à aucune demi-journée : "
            + ", ".join(str(s + 1) for s in sorted(manquantes)))

    for jour, seances in grille.fermetures:
        if not 0 <= jour < len(grille.jours):
            raise ValueError(
                f"Fermeture sur un jour inexistant (index {jour}).")
        for s in seances:
            if not 0 <= s < nb_seances:
                raise ValueError(
                    f"Fermeture sur la séance {s + 1}, inexistante.")

    ouverts = len(grille.jours) * nb_seances - sum(
        len(s) for _, s in grille.fermetures)
    if ouverts <= 0:
        raise ValueError("La grille ne laisse aucun créneau ouvert.")


def enregistrer(db: Session, ecole_id: int,
                donnees: ParametresUpdate) -> ParametresRead:
    ligne = _entites(db, ecole_id)

    if donnees.grille is not None:
        valider_grille(donnees.grille)
        ligne.grille = donnees.grille.model_dump(mode="json")
    if donnees.ponderations is not None:
        ligne.ponderations = donnees.ponderations.model_dump(mode="json")
    if donnees.presence_minimale is not None:
        ligne.presence_minimale = dict(donnees.presence_minimale)
    if donnees.type_salle_ordinaire is not None:
        ligne.type_salle_ordinaire = donnees.type_salle_ordinaire
    if donnees.limite_secondes is not None:
        ligne.limite_secondes = donnees.limite_secondes

    db.commit()
    db.refresh(ligne)
    return lire(db, ecole_id)


def fenetres(db: Session, ecole_id: int) -> List[Dict]:
    """Fenêtres pédagogiques enregistrées, prêtes pour le solveur."""
    lignes = db.query(FenetrePedagogique).filter(
        FenetrePedagogique.ecole_id == ecole_id).all()
    return [{
        "matiere_id": f.matiere_id,
        "index_jour": f.index_jour,
        "seances_bloquees": f.seances,
        "libelle": f.libelle or "",
    } for f in lignes]
