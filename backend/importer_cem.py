"""
Import d'un établissement dans une base NEUVE, puis génération.

Déroule toute la chaîne sur la pile réelle — migrations Alembic, écriture
en base, service de génération — au lieu d'appeler le solveur en direct.
C'est ce parcours-là que suivra un établissement le jour de sa mise en
service.

    python3 importer_cem.py --base sqlite:///cem20.db
    python3 importer_cem.py --generer --limite 300
    python3 importer_cem.py --generer --completer   # recrute les manquants
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--base", default="sqlite:///cem20.db",
                           help="URL de la base à créer")
    analyseur.add_argument("--generer", action="store_true",
                           help="lancer la génération après l'import")
    analyseur.add_argument("--limite", type=int, default=300,
                           help="temps de calcul maximum, en secondes")
    analyseur.add_argument("--completer", action="store_true",
                           help="recruter les enseignants manquants au programme")
    analyseur.add_argument("--conserver", action="store_true",
                           help="ne pas repartir d'une base vide")
    args = analyseur.parse_args()

    os.environ["DATABASE_URL"] = args.base
    os.environ.setdefault("DEBUG", "true")
    if args.completer:
        os.environ["CEM_COMPLETER_EFFECTIF"] = "1"

    if args.base.startswith("sqlite:///") and not args.conserver:
        fichier = Path(args.base.replace("sqlite:///", ""))
        if fichier.exists():
            fichier.unlink()

    from app import migrations
    from app.database import SessionLocal
    from app.models.class_ import Classe
    from app.models.room import Salle
    from app.models.schedule import EmploiDuTemps
    from app.models.school import Ecole
    from app.models.subject import Matiere
    from app.models.task import TacheGeneration
    from app.models.teacher import Professeur
    from app.models.user import Utilisateur
    from app.schemas.schedule import GenererRequest
    from app.services import generation
    from app.services.auth import hacher_mot_de_passe

    from tests import donnees_cem20 as source

    print("═" * 68)
    print("  IMPORT — CEM 20 divisions, base neuve")
    print("═" * 68)

    # ── 1. Schéma ────────────────────────────────────────────────
    migrations.appliquer()
    print(f"  Schéma      : révision {migrations.revision_appliquee()} "
          f"({args.base})")

    db = SessionLocal()
    try:
        # ── 2. Établissement et compte administrateur ────────────
        ecole = Ecole(nom="CEM Ibn Khaldoun", email="direction@cem20.dz",
                      ville="Alger", wilaya="Alger")
        db.add(ecole)
        db.flush()
        db.add(Utilisateur(
            ecole_id=ecole.id, nom="Direction", prenom="Administrateur",
            email="direction@cem20.dz",
            mot_de_passe_hash=hacher_mot_de_passe("motdepasse-a-changer"),
            role="admin"))

        # ── 3. Ressources ───────────────────────────────────────
        id_matiere = {}
        for matiere in source.matieres:
            code = next(c for c, i in source.ID_MATIERE.items()
                        if i == matiere.id)
            type_salle = next(
                (l["Required_Room_Type"]
                 for niveau in source.PROGRAMME.values()
                 for c, l in niveau.items() if c == code), None)
            ligne = Matiere(ecole_id=ecole.id, nom=matiere.nom,
                            coefficient=matiere.coefficient,
                            type_salle_requis=type_salle)
            db.add(ligne)
            db.flush()
            id_matiere[matiere.id] = ligne.id

        id_salle = {}
        for salle in source.salles:
            ligne = Salle(ecole_id=ecole.id, nom=salle.nom,
                          capacite=salle.capacite, type=salle.type)
            db.add(ligne)
            db.flush()
            id_salle[salle.id] = ligne.id

        id_classe = {}
        for classe in source.classes:
            ligne = Classe(ecole_id=ecole.id, nom=classe.nom,
                           niveau=classe.niveau, effectif=classe.effectif,
                           salle_attitree_id=id_salle[classe.salle_attitree_id],
                           max_heures_par_jour=classe.max_heures_par_jour)
            db.add(ligne)
            db.flush()
            id_classe[classe.id] = ligne.id

        id_prof = {}
        for prof in source.professeurs:
            ligne = Professeur(
                ecole_id=ecole.id, nom=prof.nom, prenom=prof.prenom,
                max_heures_consecutives=prof.max_heures_consecutives,
                max_heures_par_jour=prof.max_heures_par_jour,
                max_heures_par_semaine=prof.max_heures_par_semaine,
                assure_permanences=prof.assure_permanences,
                matieres=[db.get(Matiere, id_matiere[m])
                          for m in prof.matieres_ids],
            )
            db.add(ligne)
            db.flush()
            id_prof[prof.id] = ligne.id

        edt = EmploiDuTemps(ecole_id=ecole.id, nom="Semaine type",
                            annee_scolaire="2025-2026")
        db.add(edt)
        db.commit()

        print(f"  Importé     : {len(source.classes)} divisions · "
              f"{len(source.professeurs)} enseignants · "
              f"{len(source.salles)} salles · {len(source.matieres)} matières")

        # ── 4. Services que l'effectif ne permet pas de couvrir ──
        # Générer sans eux produirait un emploi du temps amputé, et
        # personne ne le verrait : c'est bloquant.
        blocages = []
        if source.services_non_affectes:
            heures = sum(int(x.split("(")[1].split()[0])
                         for x in source.services_non_affectes)
            blocages.append(
                f"{len(source.services_non_affectes)} services non affectés "
                f"({heures} h/semaine) : aucun enseignant qualifié et "
                f"disponible pour "
                f"{', '.join(source.matieres_non_couvertes) or 'ces créneaux'}. "
                f"Complétez l'effectif, ou relancez avec --completer pour "
                f"recruter le minimum nécessaire.")
        if source.enseignants_ajoutes:
            print(f"\n  ↳ Enseignants recrutés pour combler le programme : "
                  f"{', '.join(source.enseignants_ajoutes)}")

        # ── 5. Demande de génération ────────────────────────────
        demande = GenererRequest(
            cours_requis=[{
                "classe_id": id_classe[cr.classe_id],
                "matiere_id": id_matiere[cr.matiere_id],
                "professeur_id": id_prof[cr.professeur_id],
                "heures_par_semaine": cr.heures_par_semaine,
                "nb_seances_doubles": cr.nb_seances_doubles,
                "max_heures_par_jour": cr.max_heures_par_jour,
                "couplage_id": cr.couplage_id,
                "groupe": cr.groupe,
            } for cr in source.cours_requis],
            grille={
                "jours": source.JOURS,
                "horaires": source.HORAIRES,
                "shifts": source.SHIFTS,
                "fermetures": source.FERMETURES,
            },
            fenetres_pedagogiques=[{
                "matiere_id": id_matiere[f.matiere_id],
                "index_jour": f.index_jour,
                "seances_bloquees": sorted(f.seances_bloquees),
                "libelle": f.libelle,
            } for f in source.fenetres_pedagogiques],
            presence_minimale=source.options.presence_minimale,
            type_salle_ordinaire=source.options.type_salle_ordinaire,
            limite_secondes=args.limite,
        )

        erreurs, avertissements = generation.controler(demande, ecole.id, db)
        erreurs = blocages + erreurs
        print(f"\n  DIAGNOSTIC  : {len(erreurs)} erreur(s), "
              f"{len(avertissements)} avertissement(s)")
        for message in erreurs[:6]:
            print(f"    ✗ {message}")
        for message in avertissements[:3]:
            print(f"    ! {message}")
        if len(avertissements) > 3:
            print(f"    … et {len(avertissements) - 3} autre(s)")

        if erreurs:
            print("\n  Génération refusée : corrigez les erreurs ci-dessus.")
            return 1
        if not args.generer:
            print("\n  Import terminé. Relancez avec --generer pour calculer.")
            return 0

        # ── 6. Génération par le service de tâches ──────────────
        tache = TacheGeneration(
            ecole_id=ecole.id, emploi_du_temps_id=edt.id,
            statut=TacheGeneration.EN_ATTENTE,
            requete=demande.model_dump_json())
        db.add(tache)
        db.commit()
        db.refresh(tache)

        print(f"\n  Génération lancée (tâche {tache.id}, "
              f"limite {args.limite} s)…")
        generation.soumettre(tache.id)

        dernier = None
        while True:
            time.sleep(2)
            db.expire_all()
            etat = db.get(TacheGeneration, tache.id)
            if etat.message != dernier:
                dernier = etat.message
                print(f"    {etat.message}")
            if etat.statut in TacheGeneration.STATUTS_FINAUX:
                break

        if etat.statut != TacheGeneration.TERMINEE:
            print(f"\n  ✗ {etat.statut} — {etat.message}")
            return 1

        resultat = json.loads(etat.resultat)
        print(f"\n  RÉSULTAT    : {resultat['lecons_planifiees']} leçons "
              f"({resultat['statut']}) · coût "
              f"{resultat['cout_contraintes_souples']}")
        for cle, valeur in resultat["qualite"].items():
            print(f"    {cle:<32} {valeur}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
