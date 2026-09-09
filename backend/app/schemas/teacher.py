from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProfesseurCreate(BaseModel):
    nom: str
    prenom: str
    telephone: Optional[str] = None
    email: Optional[str] = None
    max_heures_consecutives: int = 4
    max_heures_par_jour: int = 6
    max_heures_par_semaine: Optional[int] = None
    assure_permanences: bool = True
    matieres_ids: List[int] = []


class ProfesseurUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    max_heures_consecutives: Optional[int] = None
    max_heures_par_jour: Optional[int] = None
    max_heures_par_semaine: Optional[int] = None
    assure_permanences: Optional[bool] = None
    matieres_ids: Optional[List[int]] = None


class ProfesseurRead(BaseModel):
    id: int
    ecole_id: int
    nom: str
    prenom: str
    telephone: Optional[str]
    email: Optional[str]
    max_heures_consecutives: int
    max_heures_par_jour: int
    max_heures_par_semaine: Optional[int]
    assure_permanences: bool
    created_at: datetime

    model_config = {"from_attributes": True}
