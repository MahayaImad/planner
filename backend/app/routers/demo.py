"""Jeu de données de démonstration : découverte et essais."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.user import Utilisateur
from ..services import demonstration

router = APIRouter(prefix="/demonstration", tags=["Démonstration"])


class ApercuReponse(BaseModel):
    nom: str
    description: str
    matieres: int
    salles: int
    classes: int
    professeurs: int
    heures_par_classe: int
    lignes_programme: int
    lecons_a_placer: int
    fenetres_pedagogiques: int
    etablissement_deja_peuple: bool


class ChargerRequest(BaseModel):
    # Écrase les ressources existantes. Sans ce drapeau, l'API refuse
    # d'écrire dans un établissement qui contient déjà des données.
    remplacer: bool = False


@router.get("/", response_model=ApercuReponse)
def apercu(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Décrit le jeu de démonstration sans rien créer."""
    return ApercuReponse(
        **demonstration.resume(),
        etablissement_deja_peuple=demonstration.deja_peuplee(
            db, utilisateur.ecole_id),
    )


@router.post("/charger", response_model=dict, status_code=status.HTTP_201_CREATED)
def charger(
    corps: ChargerRequest,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Crée le jeu de démonstration dans l'établissement connecté.

    Refuse d'écrire par-dessus des données existantes : effacer le
    travail d'un responsable sans le lui demander serait pire que de ne
    rien faire.
    """
    if demonstration.deja_peuplee(db, utilisateur.ecole_id):
        if not corps.remplacer:
            raise HTTPException(
                status_code=409,
                detail="Cet établissement contient déjà des données. "
                       "Confirmez le remplacement pour les effacer et "
                       "installer le jeu de démonstration.",
            )
        demonstration.effacer(db, utilisateur.ecole_id)

    recapitulatif = demonstration.charger(db, utilisateur.ecole_id)
    return {
        **recapitulatif,
        "message": f"{demonstration.NOM} installé : "
                   f"{recapitulatif['classes']} divisions, "
                   f"{recapitulatif['professeurs']} enseignants, "
                   f"{recapitulatif['lignes_programme']} lignes de programme, "
                   f"{recapitulatif['lecons_a_placer']} leçons à planifier.",
    }
