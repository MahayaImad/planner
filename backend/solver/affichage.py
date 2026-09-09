"""
Affichage et export des emplois du temps.

La vue grille (jours en colonnes, séances en lignes) reproduit la
présentation utilisée dans les établissements, où les trous et les
séances doubles se repèrent d'un coup d'œil.
"""

from collections import defaultdict
from typing import Any, Dict, List, Sequence

from .models import (
    Classe, GrilleHoraire, LeconPlanifiee, Matiere, Professeur, Salle,
)


def construire_index(
    grille: GrilleHoraire,
    salles: Sequence[Salle],
    matieres: Sequence[Matiere],
    professeurs: Sequence[Professeur],
    classes: Sequence[Classe],
) -> Dict[str, Dict]:
    return {
        "grille": grille,
        "creneaux": grille.index(),
        "salles": {s.id: s for s in salles},
        "matieres": {m.id: m for m in matieres},
        "professeurs": {p.id: p for p in professeurs},
        "classes": {c.id: c for c in classes},
    }


def _abreger(texte: str, largeur: int) -> str:
    texte = texte.strip()
    if len(texte) <= largeur:
        return texte.ljust(largeur)
    return texte[:largeur - 1] + "."


def _grille_texte(grille: GrilleHoraire, cellules: Dict, titre: str,
                  largeur: int = 22) -> str:
    """cellules : (jour, creneau_id) → liste de lignes de texte."""
    jours = grille.jours
    seances = []
    vus = set()
    for creneau in grille.creneaux:
        cle = (creneau.demi_journee, creneau.index_demi_journee)
        if cle not in vus:
            vus.add(cle)
            seances.append(creneau)
    seances.sort(key=lambda c: (c.demi_journee != "matin", c.index_demi_journee))

    par_jour_seance = {}
    for creneau in grille.creneaux:
        par_jour_seance[(creneau.jour, creneau.demi_journee,
                         creneau.index_demi_journee)] = creneau.id

    lignes = []
    barre = "─" * (13 + (largeur + 3) * len(jours))
    lignes.append(f"\n╭{barre}╮")
    lignes.append(f"│ {titre.ljust(len(barre) - 2)} │")
    lignes.append(f"├{barre}┤")
    entete = "│ " + "Horaire".ljust(11) + " │ " + " │ ".join(
        _abreger(j, largeur) for j in jours) + " │"
    lignes.append(entete)
    lignes.append(f"├{barre}┤")

    demi_precedente = None
    for seance in seances:
        if demi_precedente is not None and seance.demi_journee != demi_precedente:
            lignes.append("│ " + "— pause —".ljust(11) + " │ " + " │ ".join(
                " " * largeur for _ in jours) + " │")
        demi_precedente = seance.demi_journee

        horaire = f"{seance.heure_debut}-{seance.heure_fin[:5]}"
        contenus = []
        for jour in jours:
            cid = par_jour_seance.get(
                (jour, seance.demi_journee, seance.index_demi_journee))
            contenus.append(cellules.get(cid, []))

        hauteur = max((len(c) for c in contenus), default=0) or 1
        for niveau in range(hauteur):
            gauche = horaire.ljust(11) if niveau == 0 else " " * 11
            cases = [
                _abreger(c[niveau], largeur) if niveau < len(c) else " " * largeur
                for c in contenus
            ]
            lignes.append("│ " + gauche + " │ " + " │ ".join(cases) + " │")
    lignes.append(f"╰{barre}╯")
    return "\n".join(lignes)


def afficher_par_classe(lecons: Sequence[LeconPlanifiee], idx: Dict,
                        cours_requis: Sequence = ()) -> None:
    grille = idx["grille"]
    idx_cours = {cr.id: cr for cr in cours_requis}

    # Un créneau peut porter DEUX leçons : les demi-groupes d'un fouj.
    # Les empiler, sinon l'une des deux moitiés disparaît de la grille.
    brut = defaultdict(lambda: defaultdict(list))
    for lecon in lecons:
        creneau = idx["creneaux"][lecon.creneau_id]
        brut[lecon.classe_id][creneau.id].append(lecon)

    par_classe = defaultdict(dict)
    for classe_id, par_creneau in brut.items():
        for creneau_id, groupe in par_creneau.items():
            groupe.sort(key=lambda l: idx_cours.get(
                l.cours_requis_id, None).groupe if l.cours_requis_id in idx_cours else "")
            lignes = []
            for lecon in groupe:
                matiere = idx["matieres"][lecon.matiere_id]
                prof = idx["professeurs"][lecon.professeur_id]
                salle = idx["salles"][lecon.salle_id]
                cr = idx_cours.get(lecon.cours_requis_id)
                marque = "▪" if lecon.en_seance_double else " "
                etiquette = f"[{cr.groupe}] " if cr and cr.groupe else ""
                lignes.append(f"{marque}{etiquette}{matiere.nom}")
                lignes.append(f"  {prof.nom} · {salle.nom}")
            par_classe[classe_id][creneau_id] = lignes

    for classe_id in sorted(par_classe):
        classe = idx["classes"][classe_id]
        print(_grille_texte(
            grille, par_classe[classe_id],
            f"CLASSE {classe.nom} — {classe.effectif} élèves"
            + (f" — salle {idx['salles'][classe.salle_attitree_id].nom}"
               if classe.salle_attitree_id else ""),
        ))
    print("\n  ▪ = heure d'une séance double   ·   [G1]/[G2] = demi-groupes d'un fouj")


def afficher_par_professeur(lecons: Sequence[LeconPlanifiee], idx: Dict) -> None:
    grille = idx["grille"]
    par_prof = defaultdict(dict)
    for lecon in lecons:
        creneau = idx["creneaux"][lecon.creneau_id]
        matiere = idx["matieres"][lecon.matiere_id]
        classe = idx["classes"][lecon.classe_id]
        salle = idx["salles"][lecon.salle_id]
        par_prof[lecon.professeur_id][creneau.id] = [
            f"{classe.nom} · {salle.nom}",
            f" {matiere.nom}",
        ]

    for prof_id in sorted(par_prof):
        prof = idx["professeurs"][prof_id]
        heures = sum(1 for l in lecons if l.professeur_id == prof_id)
        print(_grille_texte(
            grille, par_prof[prof_id],
            f"PROFESSEUR {prof.nom_complet} — {heures} h/semaine",
        ))


def exporter_json(lecons: Sequence[LeconPlanifiee], idx: Dict) -> List[Dict[str, Any]]:
    resultat = []
    for lecon in lecons:
        c = idx["creneaux"][lecon.creneau_id]
        m = idx["matieres"][lecon.matiere_id]
        p = idx["professeurs"][lecon.professeur_id]
        s = idx["salles"][lecon.salle_id]
        cl = idx["classes"][lecon.classe_id]
        resultat.append({
            "classe": {"id": cl.id, "nom": cl.nom, "niveau": cl.niveau},
            "matiere": {"id": m.id, "nom": m.nom},
            "professeur": {"id": p.id, "nom": p.nom_complet},
            "salle": {"id": s.id, "nom": s.nom, "type": s.type},
            "creneau": {
                "id": c.id, "jour": c.jour, "index_jour": c.index_jour,
                "demi_journee": c.demi_journee,
                "heure_debut": c.heure_debut, "heure_fin": c.heure_fin,
            },
            "seance_double": lecon.en_seance_double,
        })
    resultat.sort(key=lambda r: (
        r["classe"]["nom"], r["creneau"]["index_jour"], r["creneau"]["heure_debut"],
    ))
    return resultat
