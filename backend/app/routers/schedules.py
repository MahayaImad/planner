"""
Routes emplois du temps + déclenchement du solveur CP-SAT.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from ..config import settings
from ..models.task import TacheGeneration
from ..services import deplacement, generation, statistiques

from ..database import get_db
from ..deps import get_utilisateur_courant
from ..models.user import Utilisateur
from ..models.teacher import Professeur
from ..models.subject import Matiere
from ..models.room import Salle
from ..models.class_ import Classe
from ..models.schedule import EmploiDuTemps, Lecon
from ..models.availability import DisponibiliteProfesseur
from ..schemas import (
    EmploiDuTempsCreate, EmploiDuTempsRead, LeconRead, GenererRequest,
    DiagnosticResponse, TacheRead,
)

router = APIRouter(prefix="/emplois-du-temps", tags=["Emplois du temps"])

def _get_edt_ou_404(edt_id: int, ecole_id: int, db: Session) -> EmploiDuTemps:
    edt = db.query(EmploiDuTemps).filter(
        EmploiDuTemps.id == edt_id,
        EmploiDuTemps.ecole_id == ecole_id,
    ).first()
    if not edt:
        raise HTTPException(status_code=404, detail="Emploi du temps introuvable")
    return edt


# ── CRUD emplois du temps ────────────────────────────────────────────

@router.get("/", response_model=List[EmploiDuTempsRead])
def lister(db: Session = Depends(get_db), utilisateur: Utilisateur = Depends(get_utilisateur_courant)):
    edts = db.query(EmploiDuTemps).filter(EmploiDuTemps.ecole_id == utilisateur.ecole_id).all()
    result = []
    for edt in edts:
        edt_dict = {
            "id": edt.id, "ecole_id": edt.ecole_id, "nom": edt.nom,
            "annee_scolaire": edt.annee_scolaire, "statut": edt.statut,
            "notes": edt.notes, "created_at": edt.created_at, "updated_at": edt.updated_at,
            "nb_lecons": len(edt.lecons),
        }
        result.append(edt_dict)
    return result


@router.post("/", response_model=EmploiDuTempsRead, status_code=status.HTTP_201_CREATED)
def creer(
    donnees: EmploiDuTempsCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    edt = EmploiDuTemps(ecole_id=utilisateur.ecole_id, **donnees.model_dump())
    db.add(edt)
    db.commit()
    db.refresh(edt)
    return {**edt.__dict__, "nb_lecons": 0}


@router.delete("/{edt_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(
    edt_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    edt = _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    db.delete(edt)
    db.commit()


# ── Leçons d'un emploi du temps ────────────────────────────────────

@router.get("/{edt_id}/lecons", response_model=List[LeconRead])
def lister_lecons(
    edt_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    edt = _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    lecons = []
    for l in edt.lecons:
        lecons.append(LeconRead(
            id=l.id,
            classe_id=l.classe_id,
            matiere_id=l.matiere_id,
            professeur_id=l.professeur_id,
            salle_id=l.salle_id,
            jour=l.jour,
            heure_debut=l.heure_debut,
            heure_fin=l.heure_fin,
            classe_nom=l.classe.nom if l.classe else None,
            matiere_nom=l.matiere.nom if l.matiere else None,
            professeur_nom=l.professeur.nom_complet if l.professeur else None,
            salle_nom=l.salle.nom if l.salle else None,
        ))
    return lecons


@router.get("/{edt_id}/statistiques")
def lire_statistiques(
    edt_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Indicateurs de l'emploi du temps enregistré : service et trous de
    chaque professeur, charge des divisions, taux d'occupation.

    Recalculés à la lecture plutôt que lus dans la tâche de génération :
    un emploi du temps retouché à la main doit afficher ce qu'il est
    devenu, pas ce que le solveur avait produit.
    """
    edt = _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    return statistiques.calculer(db, utilisateur.ecole_id, edt)


class DeplacementInput(BaseModel):
    jour: str
    heure_debut: str


@router.get("/{edt_id}/lecons/{lecon_id}/creneaux")
def creneaux_possibles(
    edt_id: int,
    lecon_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Où cette leçon peut aller, et pourquoi pas ailleurs.

    Balayage de la grille, sans résolution : l'interface peut éclairer
    les cases pendant le glissement au lieu de refuser après coup.
    """
    edt = _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    try:
        return deplacement.creneaux_possibles(
            db, utilisateur.ecole_id, edt, lecon_id)
    except ValueError as erreur:
        raise HTTPException(404, str(erreur)) from erreur


@router.patch("/{edt_id}/lecons/{lecon_id}")
def deplacer_lecon(
    edt_id: int,
    lecon_id: int,
    demande: DeplacementInput,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Déplace une leçon, et son partenaire de fouj avec elle.

    Revalidé ici : l'interface a pu calculer ses cases sur un état déjà
    périmé par la retouche d'un collègue.
    """
    edt = _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    try:
        resultat = deplacement.deplacer(
            db, utilisateur.ecole_id, edt, lecon_id,
            demande.jour, demande.heure_debut)
    except ValueError as erreur:
        raise HTTPException(422, str(erreur)) from erreur
    if resultat["motif"] is not None:
        raise HTTPException(409, resultat["motif"])
    return resultat


# ── Contrôle des données, sans résolution ──────────────────────

@router.post("/{edt_id}/diagnostic", response_model=DiagnosticResponse)
def controler(
    edt_id: int,
    requete: GenererRequest,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Vérifie la cohérence des données AVANT de lancer le calcul.

    Le responsable corrige ses saisies immédiatement au lieu d'attendre
    plusieurs minutes pour découvrir que le problème était insoluble.
    """
    _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    erreurs, avertissements = generation.controler(requete, utilisateur.ecole_id, db)
    return DiagnosticResponse(
        erreurs=erreurs, avertissements=avertissements, realisable=not erreurs,
    )


# ── Génération en arrière-plan ─────────────────────────────────

def _tache_en_dict(tache: TacheGeneration) -> dict:
    return {
        "id": tache.id,
        "emploi_du_temps_id": tache.emploi_du_temps_id,
        "statut": tache.statut,
        "message": tache.message,
        "cout_courant": tache.cout_courant,
        "nb_solutions": tache.nb_solutions or 0,
        "lecons_planifiees": tache.lecons_planifiees or 0,
        "resultat": json.loads(tache.resultat) if tache.resultat else None,
        "erreurs": json.loads(tache.erreurs) if tache.erreurs else [],
        "created_at": tache.created_at,
        "started_at": tache.started_at,
        "finished_at": tache.finished_at,
        "terminee": tache.statut in TacheGeneration.STATUTS_FINAUX,
    }


def _get_tache_ou_404(tache_id: int, edt_id: int, ecole_id: int,
                      db: Session) -> TacheGeneration:
    tache = db.query(TacheGeneration).filter(
        TacheGeneration.id == tache_id,
        TacheGeneration.emploi_du_temps_id == edt_id,
        TacheGeneration.ecole_id == ecole_id,
    ).first()
    if not tache:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    return tache


@router.post("/{edt_id}/generer", response_model=TacheRead,
             status_code=status.HTTP_202_ACCEPTED)
def generer(
    edt_id: int,
    requete: GenererRequest,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Met une génération en file d'attente et rend la main immédiatement.

    Une résolution dure de quelques secondes à plusieurs minutes : la
    réponse porte l'identifiant de la tâche, que le client interroge
    ensuite pour suivre l'avancement.
    """
    _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)

    en_cours = db.query(TacheGeneration).filter(
        TacheGeneration.emploi_du_temps_id == edt_id,
        TacheGeneration.statut.notin_(TacheGeneration.STATUTS_FINAUX),
    ).first()
    if en_cours:
        raise HTTPException(
            status_code=409,
            detail=f"Une génération est déjà en cours (tâche {en_cours.id}). "
                   f"Attendez la fin ou annulez-la.",
        )

    # Borner le temps de calcul : sans plafond, un client peut
    # immobiliser une place du pool pendant des heures. La valeur nulle
    # signifie « reprendre celle des réglages », résolue à la préparation.
    if requete.limite_secondes is not None:
        requete.limite_secondes = max(
            1, min(requete.limite_secondes, settings.LIMITE_SECONDES_MAX))

    # Refuser tout de suite des données incohérentes : inutile
    # d'occuper un worker pour un problème insoluble.
    erreurs, _ = generation.controler(requete, utilisateur.ecole_id, db)
    if erreurs:
        raise HTTPException(
            status_code=422,
            detail={"message": "Les données saisies sont incohérentes.",
                    "erreurs": erreurs},
        )

    tache = TacheGeneration(
        ecole_id=utilisateur.ecole_id,
        emploi_du_temps_id=edt_id,
        statut=TacheGeneration.EN_ATTENTE,
        message="En attente d'un créneau de calcul…",
        requete=requete.model_dump_json(),
    )
    db.add(tache)
    db.commit()
    db.refresh(tache)

    generation.soumettre(tache.id)
    return _tache_en_dict(tache)


@router.get("/{edt_id}/taches", response_model=List[TacheRead])
def lister_taches(
    edt_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Historique des générations de cet emploi du temps."""
    _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    taches = db.query(TacheGeneration).filter(
        TacheGeneration.emploi_du_temps_id == edt_id,
    ).order_by(TacheGeneration.id.desc()).limit(20).all()
    return [_tache_en_dict(t) for t in taches]


@router.get("/{edt_id}/taches/{tache_id}", response_model=TacheRead)
def lire_tache(
    edt_id: int,
    tache_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """Avancement d'une génération. C'est cette route que le client interroge."""
    tache = _get_tache_ou_404(tache_id, edt_id, utilisateur.ecole_id, db)
    db.refresh(tache)
    return _tache_en_dict(tache)


@router.delete("/{edt_id}/taches/{tache_id}", response_model=TacheRead)
def annuler_tache(
    edt_id: int,
    tache_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Interrompt une génération en cours.

    L'arrêt est coopératif : le solveur s'arrête à la prochaine solution
    trouvée, sans laisser l'emploi du temps à moitié réécrit.
    """
    tache = _get_tache_ou_404(tache_id, edt_id, utilisateur.ecole_id, db)
    if tache.statut in TacheGeneration.STATUTS_FINAUX:
        raise HTTPException(status_code=409,
                            detail=f"Cette tâche est déjà {tache.statut}.")
    if not generation.annuler(tache.id):
        # Le worker n'a jamais démarré (redémarrage du serveur) :
        # clore la tâche pour ne pas bloquer les suivantes.
        tache.statut = TacheGeneration.ANNULEE
        tache.message = "Génération annulée."
        db.commit()
    db.refresh(tache)
    return _tache_en_dict(tache)
