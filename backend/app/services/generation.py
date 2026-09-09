"""
Exécution des générations d'emplois du temps en arrière-plan.

Une résolution CP-SAT dure de quelques secondes à plusieurs minutes.
La conduire dans le cycle requête/réponse monopolise un worker HTTP et
dépasse le délai d'attente du navigateur. Les demandes sont donc mises
en file, exécutées sur un pool de threads borné, et suivies en base.
"""

import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import SessionLocal
from ..models.availability import DisponibiliteProfesseur
from ..models.class_ import Classe
from ..models.room import Salle
from ..models.schedule import Lecon
from ..models.subject import Matiere
from ..models.task import TacheGeneration
from ..models.teacher import Professeur
from ..schemas.schedule import GenererRequest

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

logger = logging.getLogger(__name__)

# Chaque résolution mobilise déjà plusieurs cœurs : garder le pool étroit.
_executeur = ThreadPoolExecutor(
    max_workers=settings.GENERATIONS_SIMULTANEES,
    thread_name_prefix="generation",
)

# Demandes d'annulation en cours, par identifiant de tâche.
_annulations: Dict[int, threading.Event] = {}
_verrou = threading.Lock()


def _maintenant() -> datetime:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


# ══════════════════════════════════════════════════════════════════
#  Conversion base de données → solveur
# ══════════════════════════════════════════════════════════════════

def construire_grille(config) -> GrilleHoraire:
    return GrilleHoraire.depuis_configuration(
        jours=config.jours,
        horaires=[tuple(h) for h in config.horaires],
        shifts=[(nom, list(seances)) for nom, seances in config.shifts],
        fermetures=[(jour, list(seances)) for jour, seances in config.fermetures],
    )


def preparer(requete: GenererRequest, ecole_id: int, db: Session):
    """Charge les ressources de l'école et les convertit pour le solveur."""
    db_professeurs = db.query(Professeur).filter(Professeur.ecole_id == ecole_id).all()
    db_matieres = db.query(Matiere).filter(Matiere.ecole_id == ecole_id).all()
    db_salles = db.query(Salle).filter(Salle.ecole_id == ecole_id).all()
    db_classes = db.query(Classe).filter(Classe.ecole_id == ecole_id).all()

    if not db_salles:
        raise HTTPException(400, "Aucune salle définie pour cette école")
    if not db_professeurs:
        raise HTTPException(400, "Aucun professeur défini pour cette école")

    grille = construire_grille(requete.grille)
    creneau_par_horaire = {(c.jour, c.heure_debut): c.id for c in grille.creneaux}
    tous_creneaux = {c.id for c in grille.creneaux}

    indispos = db.query(DisponibiliteProfesseur).filter(
        DisponibiliteProfesseur.disponible == 0,
        DisponibiliteProfesseur.professeur_id.in_([p.id for p in db_professeurs]),
    ).all()
    bloques: Dict[int, set] = {}
    for d in indispos:
        creneau_id = creneau_par_horaire.get((d.jour, d.heure_debut))
        if creneau_id:
            bloques.setdefault(d.professeur_id, set()).add(creneau_id)

    salles = [SSalle(id=x.id, nom=x.nom, capacite=x.capacite, type=x.type)
              for x in db_salles]
    matieres = [SMatiere(id=x.id, nom=x.nom, coefficient=x.coefficient,
                         type_salle_requis=x.type_salle_requis)
                for x in db_matieres]
    professeurs = [
        SProfesseur(
            id=p.id, nom=p.nom, prenom=p.prenom,
            matieres_ids=[m.id for m in p.matieres],
            creneaux_disponibles=tous_creneaux - bloques.get(p.id, set()),
            max_heures_consecutives=p.max_heures_consecutives,
            max_heures_par_jour=p.max_heures_par_jour or len(requete.grille.horaires),
            max_heures_par_semaine=p.max_heures_par_semaine,
            assure_permanences=bool(p.assure_permanences),
        )
        for p in db_professeurs
    ]
    classes = [SClasse(id=c.id, nom=c.nom, niveau=c.niveau, effectif=c.effectif,
                       salle_attitree_id=c.salle_attitree_id,
                       max_heures_par_jour=(c.max_heures_par_jour
                                            or len(requete.grille.horaires)))
               for c in db_classes]

    ids_classes = {c.id for c in db_classes}
    ids_profs = {p.id for p in db_professeurs}
    par_matiere = {m.id: m for m in db_matieres}

    cours = []
    for i, cr in enumerate(requete.cours_requis, start=1):
        if cr.classe_id not in ids_classes:
            raise HTTPException(400, f"Classe {cr.classe_id} introuvable")
        if cr.matiere_id not in par_matiere:
            raise HTTPException(400, f"Matière {cr.matiere_id} introuvable")
        if cr.professeur_id not in ids_profs:
            raise HTTPException(400, f"Professeur {cr.professeur_id} introuvable")
        cours.append(SCoursRequis(
            id=i,
            classe_id=cr.classe_id,
            matiere_id=cr.matiere_id,
            professeur_id=cr.professeur_id,
            heures_par_semaine=cr.heures_par_semaine,
            type_salle_requis=par_matiere[cr.matiere_id].type_salle_requis,
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
        nb_workers=settings.SOLVEUR_THREADS,
    )
    ponderations = Ponderations(**requete.ponderations.model_dump())
    return (grille, salles, matieres, professeurs, classes, cours,
            fenetres, options, ponderations)


def controler(requete: GenererRequest, ecole_id: int, db: Session
              ) -> Tuple[List[str], List[str]]:
    """Diagnostic seul : (erreurs bloquantes, avertissements)."""
    grille, salles, matieres, profs, classes, cours, fenetres, options, _ = \
        preparer(requete, ecole_id, db)
    anomalies = diagnostiquer(grille, salles, matieres, profs, classes, cours,
                              options, fenetres)
    return ([m for n, m in anomalies if n == ERREUR],
            [m for n, m in anomalies if n != ERREUR])


# ══════════════════════════════════════════════════════════════════
#  File d'exécution
# ══════════════════════════════════════════════════════════════════

def soumettre(tache_id: int) -> None:
    """Met une tâche en file d'attente."""
    with _verrou:
        _annulations[tache_id] = threading.Event()
    _executeur.submit(_executer, tache_id)


def annuler(tache_id: int) -> bool:
    """Demande l'arrêt d'une tâche. La résolution s'interrompt proprement."""
    with _verrou:
        evenement = _annulations.get(tache_id)
    if evenement is None:
        return False
    evenement.set()
    return True


# Un rapport d'avancement toutes les deux secondes au plus : assez pour
# une barre de progression, sans marteler la base pendant la recherche.
_INTERVALLE_SUIVI = 2.0


def _rapporter(tache_id: int, **champs) -> None:
    """Écrit l'avancement via une session courte, isolée du worker."""
    db = SessionLocal()
    try:
        db.query(TacheGeneration).filter(
            TacheGeneration.id == tache_id).update(champs)
        db.commit()
    except Exception:                            # noqa: BLE001
        db.rollback()
        logger.debug("Rapport d'avancement perdu (tâche %s)", tache_id,
                     exc_info=True)
    finally:
        db.close()


def _liberer(tache_id: int) -> None:
    with _verrou:
        _annulations.pop(tache_id, None)


def _executer(tache_id: int) -> None:
    """Corps de la tâche de fond. Possède sa propre session de base."""
    db = SessionLocal()
    with _verrou:
        annulation = _annulations.get(tache_id) or threading.Event()
    try:
        tache = db.get(TacheGeneration, tache_id)
        if tache is None or annulation.is_set():
            return

        tache.statut = TacheGeneration.EN_COURS
        tache.started_at = _maintenant()
        tache.message = "Préparation des données…"
        db.commit()

        requete = GenererRequest.model_validate_json(tache.requete)
        (grille, salles, matieres, professeurs, classes, cours,
         fenetres, options, ponderations) = preparer(requete, tache.ecole_id, db)

        # Clore la transaction de lecture avant plusieurs minutes de
        # calcul : la garder ouverte verrouillerait la base pendant
        # toute la résolution.
        db.commit()

        # Le suivi passe par une session courte et dédiée. L'écrire sur
        # la session du worker mêlerait les rapports d'avancement à la
        # transaction qui persistera les leçons.
        suivi = {"solutions": 0, "dernier": -_INTERVALLE_SUIVI}

        def rappel(cout: int, secondes: float):
            suivi["solutions"] += 1
            if secondes - suivi["dernier"] < _INTERVALLE_SUIVI:
                return
            suivi["dernier"] = secondes
            _rapporter(
                tache_id,
                cout_courant=cout,
                nb_solutions=suivi["solutions"],
                message=(f"Recherche en cours — meilleure solution : "
                         f"coût {cout} après {secondes:.0f} s"),
            )

        resultat = SolveurEmploiDuTemps(
            grille=grille, salles=salles, matieres=matieres,
            professeurs=professeurs, classes=classes, cours_requis=cours,
            fenetres_pedagogiques=fenetres, options=options,
            ponderations=ponderations,
        ).resoudre(rappel=rappel, arret=annulation.is_set)

        avertissements = [m for n, m in resultat.anomalies if n != ERREUR]

        if annulation.is_set():
            tache.statut = TacheGeneration.ANNULEE
            tache.message = "Génération annulée à la demande de l'utilisateur."
        elif not resultat.reussi:
            erreurs = [m for n, m in resultat.anomalies if n == ERREUR]
            tache.statut = TacheGeneration.ECHOUEE
            tache.erreurs = json.dumps(erreurs, ensure_ascii=False)
            tache.message = (
                "Les données saisies sont incohérentes."
                if erreurs else
                "Aucune solution trouvée dans le temps imparti. Augmentez la "
                "limite de calcul ou assouplissez les contraintes."
            )
        else:
            db.query(Lecon).filter(
                Lecon.emploi_du_temps_id == tache.emploi_du_temps_id).delete()
            creneaux = grille.index()
            for lecon in resultat.lecons:
                creneau = creneaux[lecon.creneau_id]
                db.add(Lecon(
                    emploi_du_temps_id=tache.emploi_du_temps_id,
                    classe_id=lecon.classe_id,
                    matiere_id=lecon.matiere_id,
                    professeur_id=lecon.professeur_id,
                    salle_id=lecon.salle_id,
                    jour=creneau.jour,
                    heure_debut=creneau.heure_debut,
                    heure_fin=creneau.heure_fin,
                ))

            metriques = evaluer(resultat.lecons, grille, salles, matieres,
                                professeurs, classes, cours,
                                options.type_salle_ordinaire)
            metriques.permanences = len(resultat.permanences)

            tache.statut = TacheGeneration.TERMINEE
            tache.lecons_planifiees = len(resultat.lecons)
            tache.nb_solutions = suivi["solutions"]
            tache.cout_courant = resultat.valeur_objectif
            tache.message = (f"{len(resultat.lecons)} leçons planifiées "
                             f"({resultat.statut}).")
            tache.resultat = json.dumps({
                "statut": resultat.statut,
                "lecons_planifiees": len(resultat.lecons),
                "duree_construction": round(resultat.duree_construction, 2),
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
                "avertissements": avertissements,
            }, ensure_ascii=False)

        tache.finished_at = _maintenant()
        db.commit()

    except HTTPException as e:
        db.rollback()
        _echouer(db, tache_id, str(e.detail))
    except Exception as e:                      # noqa: BLE001
        db.rollback()
        logger.exception("Génération %s en échec", tache_id)
        _echouer(db, tache_id, f"Erreur interne : {type(e).__name__}")
    finally:
        db.close()
        _liberer(tache_id)


def _echouer(db: Session, tache_id: int, message: str) -> None:
    tache = db.get(TacheGeneration, tache_id)
    if tache is None:
        return
    tache.statut = TacheGeneration.ECHOUEE
    tache.message = message[:500]
    tache.finished_at = _maintenant()
    db.commit()
