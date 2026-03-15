from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class EcoleCreate(BaseModel):
    nom: str
    email: EmailStr
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    ville: Optional[str] = None
    wilaya: Optional[str] = None


class EcoleRead(BaseModel):
    id: int
    nom: str
    email: str
    adresse: Optional[str]
    telephone: Optional[str]
    ville: Optional[str]
    wilaya: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
