"""Générateur d'emplois du temps scolaires (CEM / lycée — Algérie)."""

from .models import (
    APRES_MIDI, JOURS_SEMAINE_DZ, MATIN,
    Classe, CoursRequis, Creneau, FenetrePedagogique, GrilleHoraire,
    LeconPlanifiee, Matiere,
    Options, Ponderations, Professeur, Resultat, Salle,
)
from .solveur import SolveurEmploiDuTemps
from .diagnostic import AVERTISSEMENT, ERREUR, diagnostiquer, erreurs, formater
from .qualite import Metriques, evaluer
from .affichage import (
    afficher_par_classe, afficher_par_professeur, construire_index, exporter_json,
)

__all__ = [
    "MATIN", "APRES_MIDI", "JOURS_SEMAINE_DZ",
    "Creneau", "GrilleHoraire", "Salle", "Matiere", "Professeur", "Classe",
    "FenetrePedagogique",
    "CoursRequis", "LeconPlanifiee", "Options", "Ponderations", "Resultat",
    "SolveurEmploiDuTemps",
    "diagnostiquer", "formater", "erreurs", "ERREUR", "AVERTISSEMENT",
    "evaluer", "Metriques",
    "construire_index", "afficher_par_classe", "afficher_par_professeur",
    "exporter_json",
]
