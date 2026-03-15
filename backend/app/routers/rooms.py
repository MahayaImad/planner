from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.user import Utilisateur
from ..models.room import Salle
from ..schemas import SalleCreate, SalleRead, SalleUpdate

router = APIRouter(prefix="/salles", tags=["Salles"])


def _get_ou_404(id: int, ecole_id: int, db: Session) -> Salle:
    obj = db.query(Salle).filter(Salle.id == id, Salle.ecole_id == ecole_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return obj


@router.get("/", response_model=List[SalleRead])
def lister(db: Session = Depends(get_db), utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    return db.query(Salle).filter(Salle.ecole_id == utilisateur.ecole_id).all()


@router.post("/", response_model=SalleRead, status_code=status.HTTP_201_CREATED)
def creer(donnees: SalleCreate, db: Session = Depends(get_db), utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    obj = Salle(ecole_id=utilisateur.ecole_id, **donnees.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id}", response_model=SalleRead)
def lire(id: int, db: Session = Depends(get_db), utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    return _get_ou_404(id, utilisateur.ecole_id, db)


@router.patch("/{id}", response_model=SalleRead)
def modifier(id: int, donnees: SalleUpdate, db: Session = Depends(get_db), utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    obj = _get_ou_404(id, utilisateur.ecole_id, db)
    for champ, valeur in donnees.model_dump(exclude_none=True).items():
        setattr(obj, champ, valeur)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(id: int, db: Session = Depends(get_db), utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    obj = _get_ou_404(id, utilisateur.ecole_id, db)
    db.delete(obj)
    db.commit()
