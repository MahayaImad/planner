"""
Service d'authentification.
JWT HS256 implémenté manuellement avec hmac/hashlib (pas de dépendance cryptography).
Hash bcrypt via passlib.
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import Utilisateur

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


# ── Helpers JWT HS256 pur Python ──────────────────────────────────────

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)


def _signer(msg: str, secret: str) -> str:
    return _b64url_encode(
        hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    )


def creer_token(ecole_id: int, utilisateur_id: int, email: str) -> str:
    """Crée un JWT HS256."""
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = _b64url_encode(json.dumps({
        "sub": email,
        "ecole_id": ecole_id,
        "utilisateur_id": utilisateur_id,
        "exp": int(expire.timestamp()),
    }).encode())
    sig = _signer(f"{header}.{payload}", settings.SECRET_KEY)
    return f"{header}.{payload}.{sig}"


def decoder_token(token: str) -> Optional[dict]:
    """Valide et décode un JWT. Retourne None si invalide ou expiré."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, sig = parts
        expected_sig = _signer(f"{header}.{payload}", settings.SECRET_KEY)
        if not hmac.compare_digest(sig, expected_sig):
            return None
        data = json.loads(_b64url_decode(payload))
        if data.get("exp", 0) < datetime.now(tz=timezone.utc).timestamp():
            return None
        return data
    except Exception:
        return None


# ── Mots de passe ─────────────────────────────────────────────────────

def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    return pwd_context.verify(mot_de_passe, hash)


def authentifier_utilisateur(db: Session, email: str, mot_de_passe: str) -> Optional[Utilisateur]:
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not utilisateur:
        return None
    if not verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe_hash):
        return None
    return utilisateur
