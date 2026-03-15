from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MatiereCreate(BaseModel):
    nom: str
    coefficient: float = 1.0
    type_salle_requis: Optional[str] = None  # None, "labo", "info", "sport"


class MatiereUpdate(BaseModel):
    nom: Optional[str] = None
    coefficient: Optional[float] = None
    type_salle_requis: Optional[str] = None


class MatiereRead(BaseModel):
    id: int
    ecole_id: int
    nom: str
    coefficient: float
    type_salle_requis: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
