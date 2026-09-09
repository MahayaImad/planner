"""
Génération d'un emploi du temps depuis la ligne de commande.

    python3 generer_emploi_du_temps.py                 # CEM 20 divisions, vue classes
    python3 generer_emploi_du_temps.py --prof          # vue professeurs
    python3 generer_emploi_du_temps.py --json          # export JSON
    python3 generer_emploi_du_temps.py --diagnostic    # contrôle des données seul
    python3 generer_emploi_du_temps.py --reference     # petit jeu de référence
    python3 generer_emploi_du_temps.py --limite 300    # temps de calcul (s)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from solver import (  # noqa: E402
    ERREUR, SolveurEmploiDuTemps, afficher_par_classe, afficher_par_professeur,
    construire_index, diagnostiquer, evaluer, exporter_json, formater,
)


def charger(reference: bool):
    if reference:
        from tests import donnees_test as d
        d.fenetres_pedagogiques = []
        return d, "CEM Ibn Khaldoun — jeu de référence"
    from tests import donnees_cem20 as d
    return d, "CEM 20 divisions — ALGERIAN_CEM_20CLASSES"


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--prof", action="store_true", help="vue par professeur")
    analyseur.add_argument("--json", action="store_true", help="export JSON")
    analyseur.add_argument("--diagnostic", action="store_true",
                           help="contrôler les données sans résoudre")
    analyseur.add_argument("--reference", action="store_true",
                           help="utiliser le petit jeu de référence")
    analyseur.add_argument("--limite", type=int, default=None,
                           help="temps de calcul maximum, en secondes")
    args = analyseur.parse_args()

    d, titre = charger(args.reference)
    if args.limite:
        d.options.limite_secondes = args.limite
    fenetres = getattr(d, "fenetres_pedagogiques", [])

    charge = sum(c.heures_par_semaine for c in d.cours_requis)
    print("=" * 66)
    print(f"  GÉNÉRATEUR D'EMPLOIS DU TEMPS — {titre}")
    print("=" * 66)
    print(f"  Divisions {len(d.classes):>4}   Professeurs {len(d.professeurs):>4}   "
          f"Salles {len(d.salles):>4}   Créneaux ouverts {len(d.creneaux):>4}")
    print(f"  Matières  {len(d.matieres):>4}   Cours       {len(d.cours_requis):>4}   "
          f"Fenêtres pédagogiques {len(fenetres):>4}")
    print(f"  Heures-professeur à placer : {charge}")

    anomalies = diagnostiquer(d.grille, d.salles, d.matieres, d.professeurs,
                              d.classes, d.cours_requis, d.options, fenetres)
    bloquantes = [m for n, m in anomalies if n == ERREUR]
    if anomalies:
        print(f"\n  DIAGNOSTIC — {len(bloquantes)} erreur(s), "
              f"{len(anomalies) - len(bloquantes)} avertissement(s)")
        print(formater(anomalies[:12]))
        if len(anomalies) > 12:
            print(f"      … et {len(anomalies) - 12} autre(s)")

    if args.diagnostic:
        sys.exit(1 if bloquantes else 0)
    if bloquantes:
        print("\n  ✗ Données incohérentes : corrigez les erreurs ci-dessus.")
        sys.exit(1)

    print(f"\n  Résolution en cours (limite {d.options.limite_secondes} s)…")
    solveur = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis, fenetres_pedagogiques=fenetres,
        options=d.options, ponderations=d.ponderations,
    )
    resultat = solveur.resoudre()

    print(f"  Statut {resultat.statut} · modèle monté en "
          f"{resultat.duree_construction:.1f} s · résolu en "
          f"{resultat.duree_resolution:.0f} s · "
          f"{resultat.nb_variables} variables")
    if resultat.valeur_objectif is not None:
        print(f"  Coût des contraintes souples : {resultat.valeur_objectif}")

    if not resultat.reussi:
        print("\n  ✗ Aucune solution trouvée dans le temps imparti.")
        sys.exit(1)

    metriques = evaluer(resultat.lecons, d.grille, d.salles, d.matieres,
                        d.professeurs, d.classes, d.cours_requis,
                        d.options.type_salle_ordinaire)
    metriques.permanences = len(resultat.permanences)
    print(f"\n  QUALITÉ DE L'EMPLOI DU TEMPS\n{metriques.resume()}")

    idx = construire_index(d.grille, d.salles, d.matieres, d.professeurs, d.classes)
    if args.json:
        donnees = exporter_json(resultat.lecons, idx)
        chemin = Path("emploi_du_temps.json")
        chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        print(f"\n  Exporté → {chemin} ({len(donnees)} leçons)")
    elif args.prof:
        afficher_par_professeur(resultat.lecons, idx)
    else:
        afficher_par_classe(resultat.lecons, idx, d.cours_requis)

    print("\n  ✓ Emploi du temps généré.")


if __name__ == "__main__":
    main()
