"""
Script principal : génère et affiche l'emploi du temps de l'école Ibn Khaldoun.
Usage : python generer_emploi_du_temps.py [--json]
"""

import sys
import json
import time

# Rendre le dossier backend importable
sys.path.insert(0, __file__.rsplit("/", 1)[0])

from tests.donnees_test import (
    creneaux, salles, matieres, professeurs, classes, cours_requis
)
from solver import (
    SolveurEmploiDuTemps,
    construire_index,
    afficher_par_classe,
    afficher_par_professeur,
    exporter_json,
)


def main():
    export_json = "--json" in sys.argv
    vue_prof = "--prof" in sys.argv

    print("=" * 60)
    print("  GÉNÉRATEUR D'EMPLOIS DU TEMPS — Ibn Khaldoun, Alger")
    print("=" * 60)
    print(f"\n  Classes     : {len(classes)}")
    print(f"  Professeurs : {len(professeurs)}")
    print(f"  Matières    : {len(matieres)}")
    print(f"  Salles      : {len(salles)}")
    print(f"  Créneaux    : {len(creneaux)} / semaine")
    print(f"  Cours req.  : {len(cours_requis)}")
    print(f"  Leçons tot. : {sum(c.heures_par_semaine for c in cours_requis)}")
    print()

    solveur = SolveurEmploiDuTemps(
        creneaux=creneaux,
        salles=salles,
        matieres=matieres,
        professeurs=professeurs,
        classes=classes,
        cours_requis=cours_requis,
        limite_secondes=120,
    )

    print("  Résolution en cours...")
    debut = time.time()
    statut, lecons = solveur.resoudre()
    duree = time.time() - debut

    print(f"  Statut      : {statut}")
    print(f"  Durée       : {duree:.2f}s")
    print(f"  Leçons planifiées : {len(lecons)}")

    if not lecons:
        print("\n  ✗ Aucune solution trouvée. Vérifiez les contraintes.")
        sys.exit(1)

    idx = construire_index(creneaux, salles, matieres, professeurs, classes)

    if export_json:
        data = exporter_json(lecons, idx)
        output_path = "emploi_du_temps.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n  Exporté → {output_path} ({len(data)} leçons)")
    elif vue_prof:
        afficher_par_professeur(lecons, idx)
    else:
        afficher_par_classe(lecons, idx)

    print("\n  ✓ Emploi du temps généré avec succès.")


if __name__ == "__main__":
    main()
