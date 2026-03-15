from pydantic import BaseModel, EmailStr
from typing import Optional


class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    mot_de_passe: str
    role: str = "admin"


class UtilisateurRead(BaseModel):
    id: int
    ecole_id: int
    nom: str
    prenom: str
    email: str
    role: str
    actif: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utilisateur: UtilisateurRead
