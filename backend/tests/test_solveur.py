"""
Tests du solveur.

`valider` re-vérifie la solution à partir des données d'entrée, sans
faire confiance au modèle CP-SAT : c'est un contrôle indépendant que
les contraintes dures sont bien respectées.

    python3 -m pytest tests/ -q     (ou : python3 tests/test_solveur.py)
"""

import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solver import (  # noqa: E402
    Classe, CoursRequis, GrilleHoraire, JOURS_SEMAINE_DZ, Matiere, Options,
    Ponderations, Professeur, Salle, SolveurEmploiDuTemps, diagnostiquer,
    erreurs, evaluer,
)
from solver.models import LeconPlanifiee  # noqa: E402


# ══════════════════════════════════════════════════════════════════
#  Validateur indépendant
# ══════════════════════════════════════════════════════════════════

def valider(
    lecons: Sequence[LeconPlanifiee],
    grille: GrilleHoraire,
    salles, matieres, professeurs, classes, cours_requis,
    options: Options,
) -> List[str]:
    """Retourne la liste des violations de contraintes dures."""
    idx_creneaux = grille.index()
    idx_salles = {s.id: s for s in salles}
    idx_matieres = {m.id: m for m in matieres}
    idx_profs = {p.id: p for p in professeurs}
    idx_classes = {c.id: c for c in classes}
    idx_cours = {cr.id: cr for cr in cours_requis}
    violations: List[str] = []

    # Volumes horaires
    compte = defaultdict(int)
    for l in lecons:
        compte[l.cours_requis_id] += 1
    for cr in cours_requis:
        if compte[cr.id] != cr.heures_par_semaine:
            violations.append(
                f"D1 volume : cours #{cr.id} placé {compte[cr.id]} fois "
                f"au lieu de {cr.heures_par_semaine}")

    # Exclusivité classe / professeur / salle
    # Une classe peut porter deux leçons au même créneau si — et seulement
    # si — ce sont les deux demi-groupes d'un même fouj.
    activites = defaultdict(set)
    for l in lecons:
        cr = idx_cours[l.cours_requis_id]
        activites[(l.classe_id, l.creneau_id)].add(cr.couplage_id or cr.id)
    for (classe_id, creneau_id), noyaux in activites.items():
        if len(noyaux) > 1:
            violations.append(
                f"D2 classe : {idx_classes[classe_id].nom} suit {len(noyaux)} "
                f"activités distinctes sur {idx_creneaux[creneau_id]}")

    for libelle, cle in (
        ("D3 professeur", lambda l: (l.professeur_id, l.creneau_id)),
        ("D4 salle", lambda l: (l.salle_id, l.creneau_id)),
    ):
        vus = defaultdict(list)
        for l in lecons:
            vus[cle(l)].append(l)
        for k, groupe in vus.items():
            if len(groupe) > 1:
                violations.append(f"{libelle} : {len(groupe)} cours simultanés {k}")

    for l in lecons:
        creneau = idx_creneaux[l.creneau_id]
        prof = idx_profs[l.professeur_id]
        classe = idx_classes[l.classe_id]
        salle = idx_salles[l.salle_id]
        cr = idx_cours[l.cours_requis_id]
        matiere = idx_matieres[l.matiere_id]

        # D5 disponibilité
        if not prof.est_disponible(l.creneau_id):
            violations.append(
                f"D5 disponibilité : {prof.nom_complet} placé sur {creneau}")

        # D6 salle compatible
        type_requis = cr.type_salle_requis or matiere.type_salle_requis
        if type_requis == options.type_salle_ordinaire:
            type_requis = None
        if type_requis and salle.type != type_requis:
            violations.append(
                f"D6 salle : {matiere.nom} exige « {type_requis} », "
                f"placé en {salle.nom} ({salle.type})")
        if not type_requis:
            partenaire_fouj = bool(cr.couplage_id) and cr.groupe not in ("", "G1")
            if options.salle_attitree and classe.salle_attitree_id \
                    and not partenaire_fouj \
                    and l.salle_id != classe.salle_attitree_id:
                violations.append(
                    f"D6 salle attitrée : {classe.nom} en {salle.nom} "
                    f"au lieu de sa salle attitrée")
            if options.reserver_salles_specialisees \
                    and salle.type != options.type_salle_ordinaire:
                violations.append(
                    f"D6 salle : cours ordinaire de {classe.nom} en {salle.nom}")
        if options.verifier_capacite_salle:
            effectif = cr.effectif or classe.effectif
            if effectif > salle.capacite and l.salle_id != classe.salle_attitree_id:
                violations.append(
                    f"D6 capacité : {classe.nom} ({effectif}) en {salle.nom} "
                    f"({salle.capacite} places)")

        # Compétence
        if options.verifier_competence_professeur and prof.matieres_ids \
                and l.matiere_id not in prof.matieres_ids:
            violations.append(
                f"{prof.nom_complet} n'enseigne pas {matiere.nom}")

    # D7 heures consécutives / D8 heures par jour — professeurs
    par_prof_dj = defaultdict(set)
    par_prof_jour = defaultdict(set)
    for l in lecons:
        c = idx_creneaux[l.creneau_id]
        par_prof_dj[(l.professeur_id, c.jour, c.demi_journee)].add(c.index_demi_journee)
        par_prof_jour[(l.professeur_id, c.jour)].add(c.id)
    for (prof_id, jour, _), positions in par_prof_dj.items():
        prof = idx_profs[prof_id]
        indices = sorted(positions)
        serie = 1
        for a, b in zip(indices, indices[1:]):
            serie = serie + 1 if b == a + 1 else 1
            if serie > prof.max_heures_consecutives:
                violations.append(
                    f"D7 : {prof.nom_complet} enchaîne {serie} h le {jour} "
                    f"(max {prof.max_heures_consecutives})")
                break
    for (prof_id, jour), creneaux_occupes in par_prof_jour.items():
        prof = idx_profs[prof_id]
        n = len(creneaux_occupes)
        if n > prof.max_heures_par_jour:
            violations.append(
                f"D8 : {prof.nom_complet} a {n} h le {jour} "
                f"(max {prof.max_heures_par_jour})")

    # D13 jours de présence
    jours_prof = defaultdict(set)
    for l in lecons:
        jours_prof[l.professeur_id].add(idx_creneaux[l.creneau_id].jour)
    for prof in professeurs:
        if prof.max_jours_presence is not None:
            n = len(jours_prof.get(prof.id, ()))
            if n > prof.max_jours_presence:
                violations.append(
                    f"D13 : {prof.nom_complet} présent {n} jours "
                    f"(max {prof.max_jours_presence})")

    # D8 heures par jour / D12 trous — classes
    # Un fouj occupe la classe une seule fois : dédoublonner par créneau.
    par_classe_jour = defaultdict(set)
    par_classe_dj = defaultdict(set)
    for l in lecons:
        c = idx_creneaux[l.creneau_id]
        par_classe_jour[(l.classe_id, c.jour)].add(c.id)
        par_classe_dj[(l.classe_id, c.jour, c.demi_journee)].add(c.index_demi_journee)
    for (classe_id, jour), creneaux_occupes in par_classe_jour.items():
        classe = idx_classes[classe_id]
        n = len(creneaux_occupes)
        if n > classe.max_heures_par_jour:
            violations.append(
                f"D8 : {classe.nom} a {n} h le {jour} (max {classe.max_heures_par_jour})")
    if options.zero_trou_classes:
        for (classe_id, jour, demi), positions in par_classe_dj.items():
            indices = sorted(positions)
            attendu = max(indices) - min(indices) + 1
            if attendu != len(indices):
                violations.append(
                    f"D12 trou : {idx_classes[classe_id].nom} le {jour} ({demi})")

    # D9 répartition / D11 regroupement
    par_cours_jour = defaultdict(list)
    for l in lecons:
        c = idx_creneaux[l.creneau_id]
        par_cours_jour[(l.cours_requis_id, c.jour)].append(c.index_dans_jour)
    for (cr_id, jour), indices in par_cours_jour.items():
        cr = idx_cours[cr_id]
        if len(indices) > cr.max_heures_par_jour:
            violations.append(
                f"D9 : cours #{cr_id} {len(indices)} h le {jour} "
                f"(max {cr.max_heures_par_jour})")
        if options.grouper_matiere_meme_jour and len(indices) > 1:
            if max(indices) - min(indices) + 1 != len(indices):
                violations.append(
                    f"D11 : {idx_matieres[cr.matiere_id].nom} de "
                    f"{idx_classes[cr.classe_id].nom} éclatée le {jour}")

    # D10 séances doubles : accolées et dans la même salle
    doubles = defaultdict(list)
    for l in lecons:
        if l.en_seance_double:
            c = idx_creneaux[l.creneau_id]
            doubles[(l.cours_requis_id, c.jour, c.demi_journee)].append(l)
    blocs = defaultdict(int)
    for (cr_id, jour, _), groupe in doubles.items():
        groupe.sort(key=lambda l: idx_creneaux[l.creneau_id].index_demi_journee)
        indices = [idx_creneaux[l.creneau_id].index_demi_journee for l in groupe]
        if max(indices) - min(indices) + 1 != len(indices):
            violations.append(f"D10 : bloc double non contigu (cours #{cr_id}, {jour})")
        if len({l.salle_id for l in groupe}) > 1:
            violations.append(f"D10 : bloc double sur deux salles (cours #{cr_id}, {jour})")
        blocs[cr_id] += len(groupe) // 2
    for cr in cours_requis:
        if cr.nb_seances_doubles and blocs[cr.id] < cr.nb_seances_doubles:
            violations.append(
                f"D10 : cours #{cr.id} a {blocs[cr.id]} séance(s) double(s) "
                f"au lieu de {cr.nb_seances_doubles}")

    return violations


# ══════════════════════════════════════════════════════════════════
#  Tests
# ══════════════════════════════════════════════════════════════════

def _cem_reference():
    from tests import donnees_test as d
    return d


def test_diagnostic_accepte_le_jeu_de_reference():
    d = _cem_reference()
    anomalies = diagnostiquer(d.grille, d.salles, d.matieres, d.professeurs,
                              d.classes, d.cours_requis, d.options)
    assert erreurs(anomalies) == [], erreurs(anomalies)


def test_diagnostic_detecte_prof_non_competent():
    d = _cem_reference()
    cours = list(d.cours_requis)
    cours[0] = CoursRequis(id=cours[0].id, classe_id=cours[0].classe_id,
                           matiere_id=d.M_ARTS, professeur_id=cours[0].professeur_id,
                           heures_par_semaine=2)
    anomalies = diagnostiquer(d.grille, d.salles, d.matieres, d.professeurs,
                              d.classes, cours, d.options)
    assert any("n'enseigne pas" in m for m in erreurs(anomalies))


def test_diagnostic_detecte_surcharge_classe():
    grille = GrilleHoraire.construire(jours=["Dimanche"],
                                      seances_matin=[("08:00", "09:00")],
                                      seances_apres_midi=[])
    classes = [Classe(1, "1AM A", effectif=30, salle_attitree_id=1)]
    salles = [Salle(1, "S1", 40)]
    matieres = [Matiere(1, "Maths")]
    profs = [Professeur(1, "X", "Y", matieres_ids=[1])]
    cours = [CoursRequis(1, 1, 1, 1, heures_par_semaine=10)]
    messages = erreurs(diagnostiquer(grille, salles, matieres, profs, classes, cours))
    assert any("créneaux" in m or "plafond" in m for m in messages), messages


def test_diagnostic_detecte_salle_attitree_partagee():
    d = _cem_reference()
    classes = list(d.classes)
    classes[1] = Classe(id=classes[1].id, nom=classes[1].nom, niveau=classes[1].niveau,
                        effectif=classes[1].effectif,
                        salle_attitree_id=classes[0].salle_attitree_id)
    anomalies = diagnostiquer(d.grille, d.salles, d.matieres, d.professeurs,
                              classes, d.cours_requis, d.options)
    assert any("attitrée à plusieurs classes" in m for m in erreurs(anomalies))


def test_cem_complet_respecte_toutes_les_contraintes_dures():
    d = _cem_reference()
    options = Options(limite_secondes=60)
    solveur = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis, options=options,
        ponderations=Ponderations(),
    )
    resultat = solveur.resoudre()
    assert resultat.reussi, resultat.statut

    violations = valider(resultat.lecons, d.grille, d.salles, d.matieres,
                         d.professeurs, d.classes, d.cours_requis, options)
    assert violations == [], "\n".join(violations[:15])

    metriques = evaluer(resultat.lecons, d.grille, d.salles, d.matieres,
                        d.professeurs, d.classes, d.cours_requis)
    assert metriques.complet
    assert metriques.trous_classes == 0
    assert metriques.depassements_capacite == 0
    assert metriques.salles_specialisees_gaspillees == 0
    assert metriques.max_matiere_par_jour <= 2
    assert metriques.matiere_dispersee_dans_journee == 0


def test_construction_du_modele_reste_rapide():
    """Le montage du modèle ne doit pas dominer le temps de calcul."""
    d = _cem_reference()
    solveur = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis, options=Options(limite_secondes=10),
    )
    resultat = solveur.resoudre()
    assert resultat.duree_construction < 5.0, resultat.duree_construction


def test_indisponibilites_sont_respectees():
    d = _cem_reference()
    solveur = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis, options=Options(limite_secondes=30),
    )
    resultat = solveur.resoudre()
    assert resultat.reussi
    idx = d.grille.index()
    for prof in d.professeurs:
        if not prof.creneaux_disponibles:
            continue
        for lecon in resultat.lecons:
            if lecon.professeur_id == prof.id:
                assert lecon.creneau_id in prof.creneaux_disponibles, (
                    f"{prof.nom_complet} placé sur {idx[lecon.creneau_id]}")


# ── CEM réel à 20 divisions ───────────────────────────────────────

def _cem20():
    from tests import donnees_cem20 as d
    return d


def test_cem20_donnees_coherentes():
    d = _cem20()
    anomalies = diagnostiquer(d.grille, d.salles, d.matieres, d.professeurs,
                              d.classes, d.cours_requis, d.options,
                              d.fenetres_pedagogiques)
    assert erreurs(anomalies) == [], erreurs(anomalies)
    assert len(d.grille.creneaux) == 32      # mardi après-midi fermé
    assert all(c.jour != "Mardi" or c.index_seance < 4 for c in d.grille.creneaux)


def test_cem20_est_resolu_et_respecte_les_contraintes_dures():
    d = _cem20()
    d.options.limite_secondes = 150
    resultat = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis,
        fenetres_pedagogiques=d.fenetres_pedagogiques,
        options=d.options, ponderations=d.ponderations,
    ).resoudre()
    assert resultat.reussi, resultat.statut

    violations = valider(resultat.lecons, d.grille, d.salles, d.matieres,
                         d.professeurs, d.classes, d.cours_requis, d.options)
    assert violations == [], "\n".join(violations[:15])

    metriques = evaluer(resultat.lecons, d.grille, d.salles, d.matieres,
                        d.professeurs, d.classes, d.cours_requis,
                        d.options.type_salle_ordinaire)
    assert metriques.complet
    assert metriques.trous_classes == 0
    assert metriques.max_matiere_par_jour <= 2
    assert metriques.matiere_dispersee_dans_journee == 0
    # Chaque division reste dans sa salle attitrée : elle n'en fréquente
    # d'autres que pour le laboratoire, l'informatique et le stade.
    assert max(metriques.salles_par_classe.values()) <= 6
    # Une journée d'élève ne dépasse jamais la grille horaire.
    assert metriques.charge_journaliere_max <= len(d.HORAIRES)


def test_cem20_fenetres_pedagogiques_respectees():
    d = _cem20()
    d.options.limite_secondes = 60
    resultat = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis,
        fenetres_pedagogiques=d.fenetres_pedagogiques,
        options=d.options, ponderations=d.ponderations,
    ).resoudre()
    assert resultat.reussi
    idx = d.grille.index()
    interdits = {
        (f.matiere_id, f.index_jour, seance)
        for f in d.fenetres_pedagogiques for seance in f.seances_bloquees
    }
    for lecon in resultat.lecons:
        creneau = idx[lecon.creneau_id]
        cle = (lecon.matiere_id, creneau.index_jour, creneau.index_seance)
        assert cle not in interdits, f"Fenêtre pédagogique violée : {cle}"


def test_cem20_fouj_synchrones_et_dans_deux_salles():
    """Les deux demi-groupes d'un fouj partagent le créneau, pas la salle."""
    d = _cem20()
    d.options.limite_secondes = 60
    resultat = SolveurEmploiDuTemps(
        grille=d.grille, salles=d.salles, matieres=d.matieres,
        professeurs=d.professeurs, classes=d.classes,
        cours_requis=d.cours_requis,
        fenetres_pedagogiques=d.fenetres_pedagogiques,
        options=d.options, ponderations=d.ponderations,
    ).resoudre()
    assert resultat.reussi

    idx_cours = {cr.id: cr for cr in d.cours_requis}
    par_couplage = defaultdict(list)
    for lecon in resultat.lecons:
        cr = idx_cours[lecon.cours_requis_id]
        if cr.couplage_id:
            par_couplage[cr.couplage_id].append((cr, lecon))

    assert par_couplage, "aucun fouj planifié"
    for couplage, elements in par_couplage.items():
        par_groupe = defaultdict(set)
        salles_par_creneau = defaultdict(set)
        for cr, lecon in elements:
            par_groupe[cr.groupe].add(lecon.creneau_id)
            salles_par_creneau[lecon.creneau_id].add(lecon.salle_id)
        creneaux = list(par_groupe.values())
        assert all(c == creneaux[0] for c in creneaux), (
            f"{couplage} : demi-groupes désynchronisés")
        for creneau_id, salles_utilisees in salles_par_creneau.items():
            assert len(salles_utilisees) == 2, (
                f"{couplage} : les deux demi-groupes partagent une salle")


def test_probleme_infaisable_retourne_un_diagnostic_lisible():
    grille = GrilleHoraire.construire(jours=["Dimanche", "Lundi"],
                                      seances_matin=[("08:00", "09:00")],
                                      seances_apres_midi=[])
    classes = [Classe(1, "1AM A", effectif=30, salle_attitree_id=1)]
    salles = [Salle(1, "S1", 40)]
    matieres = [Matiere(1, "Physique", type_salle_requis="labo")]
    profs = [Professeur(1, "X", "Y", matieres_ids=[1])]
    cours = [CoursRequis(1, 1, 1, 1, heures_par_semaine=2)]
    resultat = SolveurEmploiDuTemps(
        grille=grille, salles=salles, matieres=matieres, professeurs=profs,
        classes=classes, cours_requis=cours).resoudre()
    assert not resultat.reussi
    assert any("labo" in m for _, m in resultat.anomalies)


if __name__ == "__main__":
    import time
    echecs = 0
    for nom, fonction in sorted(globals().items()):
        if not nom.startswith("test_") or not callable(fonction):
            continue
        depart = time.perf_counter()
        try:
            fonction()
            print(f"  ✓ {nom}  ({time.perf_counter() - depart:.1f}s)")
        except AssertionError as e:
            echecs += 1
            print(f"  ✗ {nom}\n      {e}")
    print(f"\n{'Tous les tests passent.' if not echecs else f'{echecs} échec(s).'}")
    sys.exit(1 if echecs else 0)
