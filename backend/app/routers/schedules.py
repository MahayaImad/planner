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
    EmploiDuTempsCreate, EmploiDuTempsRead, LeconRead, GenererRequest,
    DiagnosticResponse,
)

from solver import (
    ERREUR,
    Classe as SClasse,
    CoursRequis as SCoursRequis,
    FenetrePedagogique as SFenetre,
    GrilleHoraire,
    Matiere as SMatiere,
    Options,
    Ponderations,
    Professeur as SProfesseur,
    Salle as SSalle,
    SolveurEmploiDuTemps,
    diagnostiquer,
    evaluer,
)

router = APIRouter(prefix="/emplois-du-temps", tags=["Emplois du temps"])

def _construire_grille(config) -> GrilleHoraire:
    """Grille horaire de l'établissement, telle que transmise par le client."""
    return GrilleHoraire.depuis_configuration(
        jours=config.jours,
        horaires=[tuple(h) for h in config.horaires],
        shifts=[(nom, list(seances)) for nom, seances in config.shifts],
        fermetures=[(jour, list(seances)) for jour, seances in config.fermetures],
    )


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


# ── Préparation des données du solveur ─────────────────────────

def _preparer(requete: GenererRequest, ecole_id: int, db: Session):
    """Charge les ressources de l'école et les convertit pour le solveur."""
    db_professeurs = db.query(Professeur).filter(Professeur.ecole_id == ecole_id).all()
    db_matieres = db.query(Matiere).filter(Matiere.ecole_id == ecole_id).all()
    db_salles = db.query(Salle).filter(Salle.ecole_id == ecole_id).all()
    db_classes = db.query(Classe).filter(Classe.ecole_id == ecole_id).all()

    if not db_salles:
        raise HTTPException(status_code=400, detail="Aucune salle définie pour cette école")
    if not db_professeurs:
        raise HTTPException(status_code=400, detail="Aucun professeur défini pour cette école")

    grille = _construire_grille(requete.grille)
    creneau_map = {(c.jour, c.heure_debut): c.id for c in grille.creneaux}
    tous_creneaux = {c.id for c in grille.creneaux}

    # Indisponibilités → créneaux où le professeur peut enseigner.
    indispos = db.query(DisponibiliteProfesseur).filter(
        DisponibiliteProfesseur.disponible == 0,
        DisponibiliteProfesseur.professeur_id.in_([p.id for p in db_professeurs]),
    ).all()
    bloques = {}
    for d in indispos:
        cid = creneau_map.get((d.jour, d.heure_debut))
        if cid:
            bloques.setdefault(d.professeur_id, set()).add(cid)

    s_salles = [SSalle(id=x.id, nom=x.nom, capacite=x.capacite, type=x.type)
                for x in db_salles]
    s_matieres = [SMatiere(id=x.id, nom=x.nom, coefficient=x.coefficient,
                           type_salle_requis=x.type_salle_requis)
                  for x in db_matieres]
    s_professeurs = [
        SProfesseur(
            id=p.id, nom=p.nom, prenom=p.prenom,
            matieres_ids=[m.id for m in p.matieres],
            creneaux_disponibles=tous_creneaux - bloques.get(p.id, set()),
            max_heures_consecutives=p.max_heures_consecutives,
        )
        for p in db_professeurs
    ]
    s_classes = [SClasse(id=c.id, nom=c.nom, niveau=c.niveau, effectif=c.effectif,
                         max_heures_par_jour=len(requete.grille.horaires))
                 for c in db_classes]

    ids_classes = {c.id for c in db_classes}
    ids_matieres = {m.id for m in db_matieres}
    ids_profs = {p.id for p in db_professeurs}
    matieres_par_id = {m.id: m for m in db_matieres}

    s_cours = []
    for i, cr in enumerate(requete.cours_requis, start=1):
        if cr.classe_id not in ids_classes:
            raise HTTPException(status_code=400, detail=f"Classe {cr.classe_id} introuvable")
        if cr.matiere_id not in ids_matieres:
            raise HTTPException(status_code=400, detail=f"Matière {cr.matiere_id} introuvable")
        if cr.professeur_id not in ids_profs:
            raise HTTPException(status_code=400, detail=f"Professeur {cr.professeur_id} introuvable")
        s_cours.append(SCoursRequis(
            id=i,
            classe_id=cr.classe_id,
            matiere_id=cr.matiere_id,
            professeur_id=cr.professeur_id,
            heures_par_semaine=cr.heures_par_semaine,
            type_salle_requis=matieres_par_id[cr.matiere_id].type_salle_requis,
            nb_seances_doubles=cr.nb_seances_doubles,
            max_heures_par_jour=cr.max_heures_par_jour,
            couplage_id=cr.couplage_id,
            groupe=cr.groupe,
        ))

    fenetres = [
        SFenetre(matiere_id=f.matiere_id, index_jour=f.index_jour,
                 seances_bloquees=set(f.seances_bloquees), libelle=f.libelle)
        for f in requete.fenetres_pedagogiques
    ]
    options = Options(
        limite_secondes=requete.limite_secondes,
        presence_minimale=dict(requete.presence_minimale),
        type_salle_ordinaire=requete.type_salle_ordinaire,
    )
    ponderations = Ponderations(**requete.ponderations.model_dump())

    return (grille, s_salles, s_matieres, s_professeurs, s_classes,
            s_cours, fenetres, options, ponderations)


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

    Permet au responsable de corriger ses saisies sans attendre plusieurs
    minutes pour découvrir que le problème était insoluble.
    """
    _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    donnees = _preparer(requete, utilisateur.ecole_id, db)
    grille, salles, matieres, profs, classes_, cours, fenetres, options, _ = donnees
    anomalies = diagnostiquer(grille, salles, matieres, profs, classes_, cours,
                              options, fenetres)
    erreurs = [m for n, m in anomalies if n == ERREUR]
    return DiagnosticResponse(
        erreurs=erreurs,
        avertissements=[m for n, m in anomalies if n != ERREUR],
        realisable=not erreurs,
    )


# ── Génération automatique ─────────────────────────────────────

@router.post("/{edt_id}/generer", response_model=dict)
def generer(
    edt_id: int,
    requete: GenererRequest,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_courant),
):
    """
    Lance le solveur CP-SAT et remplace les leçons de cet emploi du temps.

    En cas d'échec, renvoie le diagnostic détaillé plutôt qu'un message
    générique : le responsable sait quelle contrainte bloque.
    """
    _get_edt_ou_404(edt_id, utilisateur.ecole_id, db)
    donnees = _preparer(requete, utilisateur.ecole_id, db)
    (grille, salles, matieres, profs, classes_, cours,
     fenetres, options, ponderations) = donnees

    resultat = SolveurEmploiDuTemps(
        grille=grille, salles=salles, matieres=matieres, professeurs=profs,
        classes=classes_, cours_requis=cours, fenetres_pedagogiques=fenetres,
        options=options, ponderations=ponderations,
    ).resoudre()

    if not resultat.reussi:
        erreurs = [m for n, m in resultat.anomalies if n == ERREUR]
        raise HTTPException(
            status_code=422,
            detail={
                "statut": resultat.statut,
                "message": (
                    "Les données saisies sont incohérentes."
                    if erreurs else
                    "Aucune solution trouvée dans le temps imparti. "
                    "Augmentez la limite de calcul ou assouplissez les contraintes."
                ),
                "erreurs": erreurs,
                "avertissements": [m for n, m in resultat.anomalies if n != ERREUR],
            },
        )

    creneaux = grille.index()
    db.query(Lecon).filter(Lecon.emploi_du_temps_id == edt_id).delete()
    for lecon in resultat.lecons:
        creneau = creneaux[lecon.creneau_id]
        db.add(Lecon(
            emploi_du_temps_id=edt_id,
            classe_id=lecon.classe_id,
            matiere_id=lecon.matiere_id,
            professeur_id=lecon.professeur_id,
            salle_id=lecon.salle_id,
            jour=creneau.jour,
            heure_debut=creneau.heure_debut,
            heure_fin=creneau.heure_fin,
        ))
    db.commit()

    metriques = evaluer(resultat.lecons, grille, salles, matieres, profs,
                        classes_, cours, options.type_salle_ordinaire)
    metriques.permanences = len(resultat.permanences)

    return {
        "statut": resultat.statut,
        "lecons_planifiees": len(resultat.lecons),
        "duree_resolution": round(resultat.duree_resolution, 1),
        "cout_contraintes_souples": resultat.valeur_objectif,
        "qualite": {
            "trous_classes": metriques.trous_classes,
            "trous_professeurs": metriques.trous_professeurs,
            "trous_doubles_professeurs": metriques.trous_doubles_professeurs,
            "heures_isolees_professeurs": metriques.heures_isolees_professeurs,
            "permanences": metriques.permanences,
            "charge_journaliere_min": metriques.charge_journaliere_min,
            "charge_journaliere_max": metriques.charge_journaliere_max,
            "seances_tardives_min": metriques.seances_tardives_min,
            "seances_tardives_max": metriques.seances_tardives_max,
        },
        "avertissements": [m for n, m in resultat.anomalies if n != ERREUR],
        "message": f"Emploi du temps généré : {len(resultat.lecons)} leçons planifiées.",
    }
