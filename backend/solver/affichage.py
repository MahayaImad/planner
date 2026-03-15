"""
Affichage et export des résultats du solveur.
Fonctions pour visualiser l'emploi du temps dans le terminal
et exporter en JSON.
"""

import json
from typing import List, Dict, Any
from collections import defaultdict

from .models import (
    Creneau, Salle, Matiere, Professeur,
    Classe, LeconPlanifiee
)


def construire_index(
    creneaux: List[Creneau],
    salles: List[Salle],
    matieres: List[Matiere],
    professeurs: List[Professeur],
    classes: List[Classe],
) -> Dict[str, Dict]:
    return {
        "creneaux":    {c.id: c for c in creneaux},
        "salles":      {s.id: s for s in salles},
        "matieres":    {m.id: m for m in matieres},
        "professeurs": {p.id: p for p in professeurs},
        "classes":     {cl.id: cl for cl in classes},
    }


def afficher_par_classe(
    lecons: List[LeconPlanifiee],
    idx: Dict,
) -> None:
    """Affiche l'emploi du temps regroupé par classe dans le terminal."""
    JOURS_ORDRE = ["Samedi","Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]

    par_classe: Dict[int, Dict[str, List]] = defaultdict(lambda: defaultdict(list))
    for lecon in lecons:
        creneau = idx["creneaux"][lecon.creneau_id]
        par_classe[lecon.classe_id][creneau.jour].append(lecon)

    for classe_id, par_jour in sorted(par_classe.items()):
        classe = idx["classes"][classe_id]
        print(f"\n{'='*60}")
        print(f"  CLASSE : {classe.nom} ({classe.niveau})")
        print(f"{'='*60}")

        for jour in JOURS_ORDRE:
            lecons_du_jour = par_jour.get(jour, [])
            if not lecons_du_jour:
                continue
            lecons_du_jour.sort(key=lambda l: idx["creneaux"][l.creneau_id].heure_debut)
            print(f"\n  {jour}")
            print(f"  {'-'*40}")
            for lecon in lecons_du_jour:
                c  = idx["creneaux"][lecon.creneau_id]
                m  = idx["matieres"][lecon.matiere_id]
                p  = idx["professeurs"][lecon.professeur_id]
                s  = idx["salles"][lecon.salle_id]
                print(
                    f"  {c.heure_debut}-{c.heure_fin} | "
                    f"{m.nom:<20} | "
                    f"{p.nom_complet:<20} | "
                    f"{s.nom}"
                )


def afficher_par_professeur(
    lecons: List[LeconPlanifiee],
    idx: Dict,
) -> None:
    """Affiche l'emploi du temps regroupé par professeur."""
    JOURS_ORDRE = ["Samedi", "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]

    par_prof: Dict[int, Dict[str, List]] = defaultdict(lambda: defaultdict(list))
    for lecon in lecons:
        creneau = idx["creneaux"][lecon.creneau_id]
        par_prof[lecon.professeur_id][creneau.jour].append(lecon)

    for prof_id, par_jour in sorted(par_prof.items()):
        prof = idx["professeurs"][prof_id]
        print(f"\n{'='*60}")
        print(f"  PROFESSEUR : {prof.nom_complet}")
        print(f"{'='*60}")

        for jour in JOURS_ORDRE:
            lecons_du_jour = par_jour.get(jour, [])
            if not lecons_du_jour:
                continue
            lecons_du_jour.sort(key=lambda l: idx["creneaux"][l.creneau_id].heure_debut)
            print(f"\n  {jour}")
            print(f"  {'-'*40}")
            for lecon in lecons_du_jour:
                c  = idx["creneaux"][lecon.creneau_id]
                m  = idx["matieres"][lecon.matiere_id]
                cl = idx["classes"][lecon.classe_id]
                s  = idx["salles"][lecon.salle_id]
                print(
                    f"  {c.heure_debut}-{c.heure_fin} | "
                    f"{m.nom:<20} | "
                    f"{cl.nom:<10} | "
                    f"{s.nom}"
                )


def exporter_json(
    lecons: List[LeconPlanifiee],
    idx: Dict,
) -> List[Dict[str, Any]]:
    """Retourne l'emploi du temps complet sous forme de liste de dicts JSON."""
    resultat = []
    for lecon in lecons:
        c  = idx["creneaux"][lecon.creneau_id]
        m  = idx["matieres"][lecon.matiere_id]
        p  = idx["professeurs"][lecon.professeur_id]
        s  = idx["salles"][lecon.salle_id]
        cl = idx["classes"][lecon.classe_id]
        resultat.append({
            "classe":      {"id": cl.id, "nom": cl.nom, "niveau": cl.niveau},
            "matiere":     {"id": m.id, "nom": m.nom},
            "professeur":  {"id": p.id, "nom": p.nom_complet},
            "salle":       {"id": s.id, "nom": s.nom},
            "creneau": {
                "id":          c.id,
                "jour":        c.jour,
                "heure_debut": c.heure_debut,
                "heure_fin":   c.heure_fin,
            },
        })
    # Trier pour lisibilité
    resultat.sort(key=lambda r: (
        r["classe"]["nom"],
        r["creneau"]["jour"],
        r["creneau"]["heure_debut"],
    ))
    return resultat
