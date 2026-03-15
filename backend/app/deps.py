"""Dépendances FastAPI réutilisables."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .models.user import Utilisateur
from .services.auth import decoder_token

bearer_scheme = HTTPBearer()


def get_utilisateur_courant(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    """
    Extrait et valide le token JWT.
    Retourne l'utilisateur connecté.
    Toutes les routes protégées utilisent cette dépendance.
    """
    token = credentials.credentials
    payload = decoder_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )

    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.id == payload.get("utilisateur_id")
    ).first()

    if not utilisateur or not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable ou désactivé",
        )

    return utilisateur
