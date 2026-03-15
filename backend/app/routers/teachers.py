"""CRUD professeurs + gestion des indisponibilités."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.user import Utilisateur
from ..models.teacher import Professeur
from ..models.subject import Matiere
from ..models.availability import DisponibiliteProfesseur
from ..schemas import ProfesseurCreate, ProfesseurRead, ProfesseurUpdate
from ..schemas.availability import IndisponibilitesUpdate, DisponibiliteRead

router = APIRouter(prefix="/professeurs", tags=["Professeurs"])


def _get_prof_ou_404(prof_id: int, ecole_id: int, db: Session) -> Professeur:
    prof = db.query(Professeur).filter(
        Professeur.id == prof_id,
        Professeur.ecole_id == ecole_id,
    ).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")
    return prof


@router.get("/", response_model=List[ProfesseurRead])
def lister_professeurs(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    return db.query(Professeur).filter(Professeur.ecole_id == utilisateur.ecole_id).all()


@router.post("/", response_model=ProfesseurRead, status_code=status.HTTP_201_CREATED)
def creer_professeur(
    donnees: ProfesseurCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    matieres = []
    if donnees.matieres_ids:
        matieres = db.query(Matiere).filter(
            Matiere.id.in_(donnees.matieres_ids),
            Matiere.ecole_id == utilisateur.ecole_id,
        ).all()

    prof = Professeur(
        ecole_id=utilisateur.ecole_id,
        nom=donnees.nom,
        prenom=donnees.prenom,
        telephone=donnees.telephone,
        email=donnees.email,
        max_heures_consecutives=donnees.max_heures_consecutives,
        matieres=matieres,
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


@router.get("/{prof_id}", response_model=ProfesseurRead)
def lire_professeur(
    prof_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    return _get_prof_ou_404(prof_id, utilisateur.ecole_id, db)


@router.patch("/{prof_id}", response_model=ProfesseurRead)
def modifier_professeur(
    prof_id: int,
    donnees: ProfesseurUpdate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    prof = _get_prof_ou_404(prof_id, utilisateur.ecole_id, db)

    for champ, valeur in donnees.model_dump(exclude_none=True, exclude={"matieres_ids"}).items():
        setattr(prof, champ, valeur)

    if donnees.matieres_ids is not None:
        prof.matieres = db.query(Matiere).filter(
            Matiere.id.in_(donnees.matieres_ids),
            Matiere.ecole_id == utilisateur.ecole_id,
        ).all()

    db.commit()
    db.refresh(prof)
    return prof


@router.delete("/{prof_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_professeur(
    prof_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    prof = _get_prof_ou_404(prof_id, utilisateur.ecole_id, db)
    db.delete(prof)
    db.commit()


# ── Disponibilités ────────────────────────────────────────────────────

@router.get("/{prof_id}/indisponibilites", response_model=List[DisponibiliteRead])
def lire_indisponibilites(
    prof_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    _get_prof_ou_404(prof_id, utilisateur.ecole_id, db)
    return db.query(DisponibiliteProfesseur).filter(
        DisponibiliteProfesseur.professeur_id == prof_id,
        DisponibiliteProfesseur.disponible == 0,
    ).all()


@router.put("/{prof_id}/indisponibilites", status_code=status.HTTP_204_NO_CONTENT)
def definir_indisponibilites(
    prof_id: int,
    donnees: IndisponibilitesUpdate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Remplace toutes les indisponibilités du professeur."""
    _get_prof_ou_404(prof_id, utilisateur.ecole_id, db)

    # Supprimer les anciennes
    db.query(DisponibiliteProfesseur).filter(
        DisponibiliteProfesseur.professeur_id == prof_id
    ).delete()

    # Insérer les nouvelles
    for creneau in donnees.creneaux_indisponibles:
        db.add(DisponibiliteProfesseur(
            professeur_id=prof_id,
            jour=creneau["jour"],
            heure_debut=creneau["heure_debut"],
            disponible=0,
        ))

    db.commit()
