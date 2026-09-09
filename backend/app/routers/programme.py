"""Programme annuel : consultation, édition, import et export CSV."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.class_ import Classe
from ..models.programme import LigneProgramme
from ..models.subject import Matiere
from ..models.teacher import Professeur
from ..models.user import Utilisateur
from ..services import programme as service

router = APIRouter(prefix="/programme", tags=["Programme annuel"])

TAILLE_MAX = 2 * 1024 * 1024      # 2 Mio : largement au-delà d'un programme


class LigneInput(BaseModel):
    classe_id: int
    matiere_id: int
    professeur_id: int
    heures_par_semaine: int = Field(ge=1, le=40)
    nb_seances_doubles: int = Field(default=0, ge=0, le=10)
    max_heures_par_jour: int = Field(default=2, ge=1, le=12)
    couplage_id: Optional[str] = None
    groupe: str = ""


class LigneRead(LigneInput):
    id: int
    classe_nom: Optional[str] = None
    matiere_nom: Optional[str] = None
    professeur_nom: Optional[str] = None


def _en_lecture(l: LigneProgramme) -> LigneRead:
    return LigneRead(
        id=l.id, classe_id=l.classe_id, matiere_id=l.matiere_id,
        professeur_id=l.professeur_id,
        heures_par_semaine=l.heures_par_semaine,
        nb_seances_doubles=l.nb_seances_doubles,
        max_heures_par_jour=l.max_heures_par_jour,
        couplage_id=l.couplage_id, groupe=l.groupe or "",
        classe_nom=l.classe.nom if l.classe else None,
        matiere_nom=l.matiere.nom if l.matiere else None,
        professeur_nom=l.professeur.nom_complet if l.professeur else None,
    )


def _verifier_references(donnees: LigneInput, ecole_id: int, db: Session) -> None:
    for modele, identifiant, libelle in (
        (Classe, donnees.classe_id, "Classe"),
        (Matiere, donnees.matiere_id, "Matière"),
        (Professeur, donnees.professeur_id, "Professeur"),
    ):
        if not db.query(modele).filter(modele.id == identifiant,
                                       modele.ecole_id == ecole_id).first():
            raise HTTPException(404, f"{libelle} {identifiant} introuvable")
    if donnees.nb_seances_doubles * 2 > donnees.heures_par_semaine:
        raise HTTPException(
            422, f"{donnees.nb_seances_doubles} bloc(s) de 2 h pour un volume "
                 f"de {donnees.heures_par_semaine} h")


# ── Consultation et édition ────────────────────────────────────────

@router.get("/", response_model=List[LigneRead])
def lister(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    return [_en_lecture(l) for l in service.lignes(db, utilisateur.ecole_id)]


@router.post("/", response_model=LigneRead, status_code=status.HTTP_201_CREATED)
def ajouter(
    donnees: LigneInput,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    _verifier_references(donnees, utilisateur.ecole_id, db)
    ligne = LigneProgramme(ecole_id=utilisateur.ecole_id, **donnees.model_dump())
    db.add(ligne)
    db.commit()
    db.refresh(ligne)
    return _en_lecture(ligne)


@router.put("/{ligne_id}", response_model=LigneRead)
def modifier(
    ligne_id: int,
    donnees: LigneInput,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    ligne = db.query(LigneProgramme).filter(
        LigneProgramme.id == ligne_id,
        LigneProgramme.ecole_id == utilisateur.ecole_id).first()
    if not ligne:
        raise HTTPException(404, "Ligne de programme introuvable")
    _verifier_references(donnees, utilisateur.ecole_id, db)
    for champ, valeur in donnees.model_dump().items():
        setattr(ligne, champ, valeur)
    db.commit()
    db.refresh(ligne)
    return _en_lecture(ligne)


@router.delete("/{ligne_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(
    ligne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    ligne = db.query(LigneProgramme).filter(
        LigneProgramme.id == ligne_id,
        LigneProgramme.ecole_id == utilisateur.ecole_id).first()
    if not ligne:
        raise HTTPException(404, "Ligne de programme introuvable")
    # Supprimer une moitié de fouj laisserait l'autre orpheline.
    if ligne.couplage_id:
        for jumelle in db.query(LigneProgramme).filter(
                LigneProgramme.couplage_id == ligne.couplage_id,
                LigneProgramme.ecole_id == utilisateur.ecole_id).all():
            db.delete(jumelle)
    else:
        db.delete(ligne)
    db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def vider(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Efface tout le programme de l'établissement."""
    db.query(LigneProgramme).filter(
        LigneProgramme.ecole_id == utilisateur.ecole_id).delete()
    db.commit()


# ── Import et export CSV ───────────────────────────────────────────

@router.get("/export", response_class=PlainTextResponse)
def exporter(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Programme au format d'import : modifiable au tableur, réimportable."""
    return PlainTextResponse(
        service.exporter_csv(db, utilisateur.ecole_id),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="programme.csv"'},
    )


@router.get("/modele", response_class=PlainTextResponse)
def modele(utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    """Gabarit à compléter, avec un exemple de fouj."""
    return PlainTextResponse(
        service.modele_csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="modele-programme.csv"'},
    )


@router.post("/importer", response_model=dict)
async def importer(
    fichier: UploadFile = File(...),
    verifier_seulement: bool = False,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Remplace le programme par le contenu d'un fichier CSV.

    L'import est tout ou rien : à la moindre erreur, rien n'est écrit et
    toutes les erreurs sont rendues avec leur numéro de ligne. Un
    programme à moitié chargé serait pire qu'un import refusé — le
    responsable croirait sa saisie faite.

    verifier_seulement permet de contrôler un fichier sans l'appliquer.
    """
    brut = await fichier.read()
    if len(brut) > TAILLE_MAX:
        raise HTTPException(413, "Fichier trop volumineux (2 Mio maximum)")
    try:
        contenu = brut.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Les tableurs sous Windows produisent encore du Latin-1.
        try:
            contenu = brut.decode("latin-1")
        except UnicodeDecodeError:
            raise HTTPException(422, "Encodage du fichier illisible : "
                                     "enregistrez-le en UTF-8.")

    valides, erreurs = service.analyser_csv(db, utilisateur.ecole_id, contenu)

    if erreurs:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"{len(erreurs)} problème(s) détecté(s). "
                           f"Rien n'a été importé.",
                "erreurs": erreurs[:50],
                "erreurs_totales": len(erreurs),
                "lignes_valides": len(valides),
            },
        )

    if verifier_seulement:
        return {"lignes_valides": len(valides), "importe": False,
                "message": f"{len(valides)} lignes valides. "
                           f"Le fichier peut être importé."}

    nombre = service.remplacer(db, utilisateur.ecole_id, valides)
    return {"lignes_valides": nombre, "importe": True,
            "message": f"Programme remplacé : {nombre} lignes importées."}
