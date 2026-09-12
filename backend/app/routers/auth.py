"""Routes d'authentification : inscription école + login."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.school import Ecole
from ..models.user import Utilisateur
from ..schemas import EcoleCreate, UtilisateurCreate, LoginRequest, Token
from ..services.auth import hacher_mot_de_passe, authentifier_utilisateur, creer_token
from ..deps import get_utilisateur_courant

router = APIRouter(prefix="/auth", tags=["Authentification"])


class InscrireRequest(BaseModel):
    """Corps unique pour l'inscription : école + compte admin."""
    ecole: EcoleCreate
    admin: UtilisateurCreate


@router.post("/inscrire", response_model=Token, status_code=status.HTTP_201_CREATED)
def inscrire_ecole(body: InscrireRequest, db: Session = Depends(get_db)):
    """
    Inscrit une nouvelle école et crée le compte administrateur.
    Retourne un token JWT directement utilisable.

    Les deux adresses sont vérifiées AVANT d'écrire : celle de
    l'établissement et celle de l'administrateur portent chacune une
    contrainte d'unicité, et laisser la base les refuser produisait une
    erreur 500 illisible — un responsable qui se réinscrivait par
    mégarde voyait « erreur interne » au lieu de « vous avez déjà un
    compte ».
    """
    if db.query(Ecole).filter(Ecole.email == body.ecole.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un établissement est déjà inscrit avec cette adresse. "
                   "Connectez-vous plutôt que d'en créer un second.",
        )
    if db.query(Utilisateur).filter(
            Utilisateur.email == body.admin.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse est déjà associée à un compte. "
                   "Connectez-vous, ou utilisez une autre adresse.",
        )

    ecole = Ecole(**body.ecole.model_dump())
    db.add(ecole)
    db.flush()

    utilisateur = Utilisateur(
        ecole_id=ecole.id,
        nom=body.admin.nom,
        prenom=body.admin.prenom,
        email=body.admin.email,
        mot_de_passe_hash=hacher_mot_de_passe(body.admin.mot_de_passe),
        role="admin",
    )
    db.add(utilisateur)
    try:
        db.commit()
    except IntegrityError as erreur:
        # Deux inscriptions simultanées peuvent passer les contrôles
        # ci-dessus puis se heurter à la contrainte : la base reste
        # l'arbitre, mais le message doit rester lisible.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse est déjà associée à un compte. "
                   "Connectez-vous, ou utilisez une autre adresse.",
        ) from erreur
    db.refresh(utilisateur)

    token = creer_token(ecole.id, utilisateur.id, utilisateur.email)
    return Token(access_token=token, utilisateur=utilisateur)


@router.post("/connexion", response_model=Token)
def connexion(
    donnees: LoginRequest,
    db: Session = Depends(get_db),
):
    """Connecte un utilisateur existant. Retourne un token JWT."""
    utilisateur = authentifier_utilisateur(db, donnees.email, donnees.mot_de_passe)
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = creer_token(utilisateur.ecole_id, utilisateur.id, utilisateur.email)
    return Token(access_token=token, utilisateur=utilisateur)


@router.get("/moi", response_model=dict)
def profil(utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    """
    Profil de l'utilisateur connecté.

    Le nom de l'établissement en fait partie : l'interface l'affiche en
    permanence, et le redemander par un second appel à chaque
    démarrage n'apporterait rien.
    """
    return {
        "id": utilisateur.id,
        "email": utilisateur.email,
        "nom_complet": f"{utilisateur.prenom} {utilisateur.nom}",
        "role": utilisateur.role,
        "ecole_id": utilisateur.ecole_id,
        "ecole_nom": utilisateur.ecole.nom if utilisateur.ecole else None,
    }
