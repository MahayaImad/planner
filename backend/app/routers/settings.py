"""Réglages de planification et fenêtres pédagogiques."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.settings import FenetrePedagogique
from ..models.subject import Matiere
from ..models.user import Utilisateur
from ..schemas import (
    FenetreCreate, FenetreRead, ParametresRead, ParametresUpdate,
)
from ..services import parametres as service

router = APIRouter(tags=["Réglages"])


# ── Réglages de planification ──────────────────────────────────────

@router.get("/parametres", response_model=ParametresRead)
def lire_parametres(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Grille horaire, pondérations et présence minimale de l'établissement."""
    return service.lire(db, utilisateur.ecole_id)


@router.put("/parametres", response_model=ParametresRead)
def modifier_parametres(
    donnees: ParametresUpdate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Enregistre les réglages. Seuls les champs fournis sont modifiés.

    La grille est validée avant écriture : une grille incohérente rendrait
    toute génération impossible sans que la cause soit visible.
    """
    try:
        return service.enregistrer(db, utilisateur.ecole_id, donnees)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Fenêtres pédagogiques ──────────────────────────────────────────

def _en_lecture(fenetre: FenetrePedagogique) -> FenetreRead:
    return FenetreRead(
        id=fenetre.id,
        matiere_id=fenetre.matiere_id,
        matiere_nom=fenetre.matiere.nom if fenetre.matiere else None,
        index_jour=fenetre.index_jour,
        seances_bloquees=fenetre.seances,
        libelle=fenetre.libelle,
    )


@router.get("/fenetres-pedagogiques", response_model=List[FenetreRead])
def lister_fenetres(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    fenetres = db.query(FenetrePedagogique).filter(
        FenetrePedagogique.ecole_id == utilisateur.ecole_id,
    ).order_by(FenetrePedagogique.index_jour, FenetrePedagogique.id).all()
    return [_en_lecture(f) for f in fenetres]


@router.post("/fenetres-pedagogiques", response_model=FenetreRead,
             status_code=status.HTTP_201_CREATED)
def creer_fenetre(
    donnees: FenetreCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    matiere = db.query(Matiere).filter(
        Matiere.id == donnees.matiere_id,
        Matiere.ecole_id == utilisateur.ecole_id,
    ).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    if not donnees.seances_bloquees:
        raise HTTPException(status_code=422,
                            detail="Indiquez au moins une séance à bloquer")

    existante = db.query(FenetrePedagogique).filter(
        FenetrePedagogique.matiere_id == donnees.matiere_id,
        FenetrePedagogique.index_jour == donnees.index_jour,
    ).first()
    if existante:
        raise HTTPException(
            status_code=409,
            detail=f"Une fenêtre existe déjà pour « {matiere.nom} » ce jour-là. "
                   f"Modifiez-la ou supprimez-la d'abord.",
        )

    fenetre = FenetrePedagogique(
        ecole_id=utilisateur.ecole_id,
        matiere_id=donnees.matiere_id,
        index_jour=donnees.index_jour,
        seances_bloquees=";".join(str(s) for s in sorted(set(donnees.seances_bloquees))),
        libelle=donnees.libelle,
    )
    db.add(fenetre)
    db.commit()
    db.refresh(fenetre)
    return _en_lecture(fenetre)


@router.delete("/fenetres-pedagogiques/{fenetre_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def supprimer_fenetre(
    fenetre_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    fenetre = db.query(FenetrePedagogique).filter(
        FenetrePedagogique.id == fenetre_id,
        FenetrePedagogique.ecole_id == utilisateur.ecole_id,
    ).first()
    if not fenetre:
        raise HTTPException(status_code=404, detail="Fenêtre introuvable")
    db.delete(fenetre)
    db.commit()
