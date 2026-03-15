"""
Routes emplois du temps + déclenchement du solveur CP-SAT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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
    EmploiDuTempsCreate, EmploiDuTempsRead, LeconRead, GenererRequest
)

# Solveur Phase 1
from solver.models import (
    Creneau as SCreneau,
    Salle as SSalle,
    Matiere as SMatiere,
    Professeur as SProfesseur,
    Classe as SClasse,
    CoursRequis as SCoursRequis,
)
from solver.solveur import SolveurEmploiDuTemps

router = APIRouter(prefix="/emplois-du-temps", tags=["Emplois du temps"])

# Créneaux horaires fixes (semaine algérienne Samedi→Jeudi)
JOURS = ["Samedi", "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]
HEURES = [
    ("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00"),
    ("13:00", "14:00"), ("14:00", "15:00"), ("15:00", "16:00"), ("16:00", "17:00"),
]


def _build_creneaux() -> List[SCreneau]:
    creneaux = []
    cid = 1
    for jour in JOURS:
        for heure_debut, heure_fin in HEURES:
            creneaux.append(SCreneau(id=cid, jour=jour, heure_debut=heure_debut, heure_fin=heure_fin))
            cid += 1
    return creneaux


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


# ── Génération automatique ─────────────────────────────────────────

@router.post("/{edt_id}/generer", response_model=dict)
def generer(
    edt_id: int,
    requete: GenererRequest,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Déclenche le solveur CP-SAT pour remplir l'emploi du temps.
    Supprime les leçons existantes et les remplace par la solution.
    """
    edt = _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    ecole_id = utilisateur.ecole_id

    # Charger les entités de l'école depuis la DB
    db_professeurs = db.query(Professeur).filter(Professeur.ecole_id == ecole_id).all()
    db_matieres = db.query(Matiere).filter(Matiere.ecole_id == ecole_id).all()
    db_salles = db.query(Salle).filter(Salle.ecole_id == ecole_id).all()
    db_classes = db.query(Classe).filter(Classe.ecole_id == ecole_id).all()

    if not db_salles:
        raise HTTPException(status_code=400, detail="Aucune salle définie pour cette école")
    if not db_professeurs:
        raise HTTPException(status_code=400, detail="Aucun professeur défini pour cette école")

    # Construire les indisponibilités : créneau_id → prof_ids indisponibles
    creneaux = _build_creneaux()
    creneau_map = {(c.jour, c.heure_debut): c.id for c in creneaux}

    # Disponibilités par prof
    dispo_par_prof = {}
    for prof in db_professeurs:
        indispos = db.query(DisponibiliteProfesseur).filter(
            DisponibiliteProfesseur.professeur_id == prof.id,
            DisponibiliteProfesseur.disponible == 0,
        ).all()
        creneaux_indispo = set()
        for d in indispos:
            cid = creneau_map.get((d.jour, d.heure_debut))
            if cid:
                creneaux_indispo.add(cid)
        # creneaux_disponibles = tous les créneaux sauf les indisponibles
        dispo_par_prof[prof.id] = set(c.id for c in creneaux) - creneaux_indispo

    # Convertir en objets solveur
    s_creneaux = creneaux
    s_salles = [SSalle(id=s.id, nom=s.nom, capacite=s.capacite, type=s.type) for s in db_salles]
    s_matieres = [SMatiere(id=m.id, nom=m.nom, coefficient=m.coefficient) for m in db_matieres]
    s_professeurs = [
        SProfesseur(
            id=p.id, nom=p.nom, prenom=p.prenom,
            matieres_ids=[m.id for m in p.matieres],
            creneaux_disponibles=dispo_par_prof.get(p.id, set()),
            max_heures_consecutives=p.max_heures_consecutives,
        )
        for p in db_professeurs
    ]
    s_classes = [SClasse(id=c.id, nom=c.nom, niveau=c.niveau, effectif=c.effectif) for c in db_classes]

    # Valider les cours requis de la requête
    ids_classes = {c.id for c in db_classes}
    ids_matieres = {m.id for m in db_matieres}
    ids_profs = {p.id for p in db_professeurs}

    s_cours = []
    for i, cr in enumerate(requete.cours_requis, start=1):
        if cr.classe_id not in ids_classes:
            raise HTTPException(status_code=400, detail=f"Classe {cr.classe_id} introuvable")
        if cr.matiere_id not in ids_matieres:
            raise HTTPException(status_code=400, detail=f"Matière {cr.matiere_id} introuvable")
        if cr.professeur_id not in ids_profs:
            raise HTTPException(status_code=400, detail=f"Professeur {cr.professeur_id} introuvable")

        matiere_db = next(m for m in db_matieres if m.id == cr.matiere_id)
        s_cours.append(SCoursRequis(
            id=i,
            classe_id=cr.classe_id,
            matiere_id=cr.matiere_id,
            professeur_id=cr.professeur_id,
            heures_par_semaine=cr.heures_par_semaine,
            type_salle_requis=matiere_db.type_salle_requis,
        ))

    # Lancer le solveur
    solveur = SolveurEmploiDuTemps(
        creneaux=s_creneaux,
        salles=s_salles,
        matieres=s_matieres,
        professeurs=s_professeurs,
        classes=s_classes,
        cours_requis=s_cours,
        limite_secondes=requete.limite_secondes,
    )
    statut, lecons_solver = solveur.resoudre()

    if statut not in ("OPTIMAL", "FEASIBLE"):
        raise HTTPException(
            status_code=422,
            detail=f"Aucune solution trouvée (statut: {statut}). "
                   "Vérifiez les disponibilités et le nombre de salles.",
        )

    # Construire un index créneau_id → (jour, heure_debut, heure_fin)
    creneau_info = {c.id: c for c in creneaux}

    # Supprimer les anciennes leçons et insérer les nouvelles
    db.query(Lecon).filter(Lecon.emploi_du_temps_id == edt_id).delete()

    for l in lecons_solver:
        cr_info = creneau_info[l.creneau_id]
        db.add(Lecon(
            emploi_du_temps_id=edt_id,
            classe_id=l.classe_id,
            matiere_id=l.matiere_id,
            professeur_id=l.professeur_id,
            salle_id=l.salle_id,
            jour=cr_info.jour,
            heure_debut=cr_info.heure_debut,
            heure_fin=cr_info.heure_fin,
        ))

    db.commit()

    return {
        "statut": statut,
        "lecons_planifiees": len(lecons_solver),
        "message": f"Emploi du temps généré avec succès : {len(lecons_solver)} leçons planifiées.",
    }
