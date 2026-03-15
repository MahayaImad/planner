from pydantic import BaseModel
from typing import List


class DisponibiliteCreate(BaseModel):
    jour: str         # "Lundi"
    heure_debut: str  # "08:00"
    disponible: int = 0  # 0 = indisponible


class DisponibiliteRead(BaseModel):
    id: int
    professeur_id: int
    jour: str
    heure_debut: str
    disponible: int

    model_config = {"from_attributes": True}


class IndisponibilitesUpdate(BaseModel):
    """Remplace toutes les indisponibilités d'un prof."""
    creneaux_indisponibles: List[dict]  # [{"jour": "Lundi", "heure_debut": "08:00"}]
