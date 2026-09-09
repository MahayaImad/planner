"""
Service d'authentification.

JWT HS256 signé à la main (hmac/hashlib) pour éviter une dépendance
supplémentaire. Mots de passe hachés avec scrypt, disponible dans la
bibliothèque standard : fonction mémoire-dure, donc coûteuse à attaquer
par force brute sur GPU.
"""

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import Utilisateur

# ── Paramètres scrypt ─────────────────────────────────────────────
# n=2^15, r=8, p=1 : environ 32 Mo et ~100 ms par vérification, ce qui
# reste imperceptible à la connexion mais ruine une attaque massive.
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2 ** 15, 8, 1
_LONGUEUR_SEL, _LONGUEUR_CLE = 16, 32
# OpenSSL plafonne scrypt à 32 Mo par défaut, soit exactement ce que
# demandent ces paramètres : relever la borne, sinon l'appel échoue.
_SCRYPT_MAXMEM = 128 * _SCRYPT_N * _SCRYPT_R * 2
_PREFIXE = "scrypt"


# ── Helpers JWT HS256 ─────────────────────────────────────────────

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _signer(msg: str, secret: str) -> str:
    return _b64url_encode(
        hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    )


def creer_token(ecole_id: int, utilisateur_id: int, email: str) -> str:
    """Crée un JWT HS256."""
    header = _b64url_encode(json.dumps(
        {"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    emis_le = datetime.now(tz=timezone.utc)
    expire = emis_le + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = _b64url_encode(json.dumps({
        "sub": email,
        "ecole_id": ecole_id,
        "utilisateur_id": utilisateur_id,
        "iat": int(emis_le.timestamp()),
        "exp": int(expire.timestamp()),
    }, separators=(",", ":")).encode())
    signature = _signer(f"{header}.{payload}", settings.SECRET_KEY)
    return f"{header}.{payload}.{signature}"


def decoder_token(token: str) -> Optional[dict]:
    """Valide et décode un JWT. Retourne None si invalide ou expiré."""
    try:
        parties = token.split(".")
        if len(parties) != 3:
            return None
        header, payload, signature = parties

        # Refuser explicitement un algorithme autre que HS256 : sans ce
        # contrôle, un jeton « alg: none » resterait rejeté par la
        # signature, mais l'intention doit être lisible dans le code.
        entete = json.loads(_b64url_decode(header))
        if entete.get("alg") != "HS256" or entete.get("typ") != "JWT":
            return None

        attendue = _signer(f"{header}.{payload}", settings.SECRET_KEY)
        if not hmac.compare_digest(signature, attendue):
            return None

        donnees = json.loads(_b64url_decode(payload))
        if donnees.get("exp", 0) < datetime.now(tz=timezone.utc).timestamp():
            return None
        return donnees
    except Exception:
        return None


# ── Mots de passe ─────────────────────────────────────────────────

def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Retourne « scrypt$n$r$p$sel$empreinte », le tout en base64url."""
    sel = os.urandom(_LONGUEUR_SEL)
    empreinte = hashlib.scrypt(
        mot_de_passe.encode("utf-8"), salt=sel,
        n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=_LONGUEUR_CLE,
        maxmem=_SCRYPT_MAXMEM,
    )
    return "$".join((
        _PREFIXE, str(_SCRYPT_N), str(_SCRYPT_R), str(_SCRYPT_P),
        _b64url_encode(sel), _b64url_encode(empreinte),
    ))


def _verifier_legacy(mot_de_passe: str, empreinte: str) -> bool:
    """
    Vérifie une empreinte sha256_crypt produite par les versions
    précédentes, afin que les comptes existants puissent encore se
    connecter. Ces empreintes sont remplacées à la volée.
    """
    try:
        from passlib.hash import sha256_crypt
        return sha256_crypt.verify(mot_de_passe, empreinte)
    except Exception:
        return False


def verifier_mot_de_passe(mot_de_passe: str, empreinte: str) -> bool:
    if not empreinte:
        return False
    if not empreinte.startswith(_PREFIXE + "$"):
        return _verifier_legacy(mot_de_passe, empreinte)
    try:
        _, n, r, p, sel, attendue = empreinte.split("$")
        calculee = hashlib.scrypt(
            mot_de_passe.encode("utf-8"), salt=_b64url_decode(sel),
            n=int(n), r=int(r), p=int(p),
            dklen=len(_b64url_decode(attendue)),
            maxmem=128 * int(n) * int(r) * 2,
        )
        return hmac.compare_digest(_b64url_encode(calculee), attendue)
    except Exception:
        return False


def doit_etre_rehache(empreinte: str) -> bool:
    """Vrai si l'empreinte utilise un format ou des paramètres dépassés."""
    if not empreinte.startswith(_PREFIXE + "$"):
        return True
    try:
        _, n, r, p, _, _ = empreinte.split("$")
        return (int(n), int(r), int(p)) != (_SCRYPT_N, _SCRYPT_R, _SCRYPT_P)
    except Exception:
        return True


def authentifier_utilisateur(db: Session, email: str,
                             mot_de_passe: str) -> Optional[Utilisateur]:
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == email.lower().strip()).first()

    if utilisateur is None:
        # Consommer le même temps de calcul qu'une vérification réelle :
        # sinon la durée de réponse révèle quels comptes existent.
        hacher_mot_de_passe(mot_de_passe)
        return None

    if not verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe_hash):
        return None

    if doit_etre_rehache(utilisateur.mot_de_passe_hash):
        utilisateur.mot_de_passe_hash = hacher_mot_de_passe(mot_de_passe)
        db.commit()

    return utilisateur
