from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SalleCreate(BaseModel):
    nom: str
    capacite: int = 30
    type: str = "classique"  # classique, labo, info, sport


class SalleUpdate(BaseModel):
    nom: Optional[str] = None
    capacite: Optional[int] = None
    type: Optional[str] = None


class SalleRead(BaseModel):
    id: int
    ecole_id: int
    nom: str
    capacite: int
    type: str
    created_at: datetime

    model_config = {"from_attributes": True}
