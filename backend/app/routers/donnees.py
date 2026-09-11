"""
Chargement en masse des données d'un établissement par classeur Excel.

Trois routes seulement : télécharger un gabarit, exporter l'existant
dans le même format, et téléverser. Le gabarit et l'export partagent
la même structure, ce qui permet d'exporter, corriger au tableur, puis
re-téléverser.
"""

from fastapi import (
    APIRouter, Depends, File, HTTPException, Query, UploadFile, status,
)
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.user import Utilisateur
from ..services import classeur

router = APIRouter(prefix="/donnees", tags=["Données"])

TYPE_XLSX = ("application/vnd.openxmlformats-officedocument"
             ".spreadsheetml.sheet")


def _fichier(contenu: bytes, nom: str) -> Response:
    return Response(
        content=contenu, media_type=TYPE_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{nom}"'},
    )


@router.get("/modele.xlsx")
def modele(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Classeur vierge, avec son mode d'emploi et ses listes déroulantes."""
    return _fichier(classeur.construire(db, utilisateur.ecole_id, False),
                    "modele-etablissement.xlsx")


@router.get("/export.xlsx")
def exporter(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Données actuelles, dans le format du gabarit."""
    return _fichier(classeur.construire(db, utilisateur.ecole_id, True),
                    "donnees-etablissement.xlsx")


@router.post("/importer", status_code=status.HTTP_200_OK)
async def importer(
    fichier: UploadFile = File(...),
    apercu: bool = Query(False, description="Valider sans rien écrire."),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Téléverse un classeur. Rien n'est écrit tant qu'une seule ligne
    reste en erreur ; `apercu=true` valide sans jamais écrire.
    """
    contenu = await fichier.read()
    if not contenu:
        raise HTTPException(422, "Fichier vide.")
    if len(contenu) > classeur.TAILLE_MAX:
        raise HTTPException(
            413, f"Fichier trop volumineux ({len(contenu) // 1024} Kio).")
    return classeur.importer(db, utilisateur.ecole_id, contenu,
                             appliquer=not apercu)
