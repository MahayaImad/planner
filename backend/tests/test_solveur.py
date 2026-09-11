"""
Tests du solveur.

`valider` re-vérifie la solution à partir des données d'entrée, sans
faire confiance au modèle CP-SAT : c'est un contrôle indépendant que
les contraintes dures sont bien respectées.

    python3 -m pytest tests/ -q     (ou : python3 tests/test_solveur.py)
"""

import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Le programme est désormais entièrement couvert par les enseignants
# déclarés ; ce garde-fou reste actif au cas où une matière serait
# ajoutée sans l'effectif correspondant.
os.environ.setdefault("CEM_COMPLETER_EFFECTIF", "1")

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
            # Seul le demi-groupe porteur (G1) garde la salle attitrée.
            if cr.couplage_id:
                porteur = min(
                    (x for x in cours_requis if x.couplage_id == cr.couplage_id),
                    key=lambda x: (x.groupe or "", x.id))
                partenaire_fouj = porteur.id != cr.id
            else:
                partenaire_fouj = False
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

    # D17 service hebdomadaire
    charge_hebdo = defaultdict(set)
    for l in lecons:
        charge_hebdo[l.professeur_id].add(l.creneau_id)
    for prof in professeurs:
        plafond = prof.max_heures_par_semaine
        if plafond is not None and len(charge_hebdo.get(prof.id, ())) > plafond:
            violations.append(
                f"D17 : {prof.nom_complet} assure "
                f"{len(charge_hebdo[prof.id])} h/semaine (max {plafond})")

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
    from donnees import cem20 as d
    return d


def test_cem20_effectif_couvre_le_programme():
    """Chaque service du programme doit trouver un enseignant qualifié."""
    d = _cem20()
    assert d.services_non_affectes == [], d.services_non_affectes[:5]
    heures = sum(s[2] for s in d.services)
    assert sum(c.heures_par_semaine for c in d.cours_requis) == heures
    # Aucun service ne dépasse le plafond hebdomadaire de son titulaire.
    charge = defaultdict(int)
    for cr in d.cours_requis:
        charge[cr.professeur_id] += cr.heures_par_semaine
    for prof in d.professeurs:
        plafond = prof.max_heures_par_semaine
        if plafond is not None:
            assert charge[prof.id] <= plafond, (
                f"{prof.nom_complet} : {charge[prof.id]} h > {plafond}")


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


def test_metrique_detecte_plus_d_une_heure_creuse_par_jour():
    """
    Journée d'un enseignant : occupé, libre, occupé, libre, occupé.
    Deux heures creuses dans la même journée, donc une de trop.
    """
    horaires = [(f"{8 + i:02d}:00", f"{8 + i:02d}:55") for i in range(5)]
    grille = GrilleHoraire.depuis_configuration(
        ["Dimanche"], horaires, [("journee", list(range(5)))])
    par_seance = {c.index_seance: c.id for c in grille.creneaux}

    salles = [Salle(1, "S1", 40)]
    classes = [Classe(1, "C1", effectif=30, salle_attitree_id=1)]
    matieres = [Matiere(1, "Maths")]
    professeurs = [Professeur(1, "Unique", "Prof", matieres_ids=[1])]
    cours = [CoursRequis(1, 1, 1, 1, heures_par_semaine=3)]

    lecons = [
        LeconPlanifiee(cours_requis_id=1, classe_id=1, matiere_id=1,
                       professeur_id=1, salle_id=1,
                       creneau_id=par_seance[position])
        for position in (0, 2, 4)
    ]
    metriques = evaluer(lecons, grille, salles, matieres, professeurs,
                        classes, cours)
    assert metriques.trous_professeurs == 2
    assert metriques.journees_hachees_professeurs == 1
    assert metriques.heures_creuses_en_trop == 1
    # Deux coupures séparées d'une heure, donc aucun vide de deux heures.
    assert metriques.trous_doubles_professeurs == 0
    assert metriques.coupures_en_trop == 1


def test_heure_creuse_avant_le_dejeuner_est_comptee():
    """
    Journée d'un enseignant : cours, libre, cours, libre, puis cours et
    cours l'après-midi.

    La séance libre juste avant le déjeuner tombe après le dernier cours
    du matin : le découpage en demi-journées ne la voit pas. Du point de
    vue de l'enseignant, sa journée est pourtant trouée deux fois — il
    est sur place de 8 h à 15 h avec deux séances vides.
    """
    horaires = [("08:00", "08:55"), ("09:00", "09:55"), ("10:05", "11:00"),
                ("11:05", "12:00"), ("13:00", "13:55"), ("14:00", "14:55"),
                ("15:05", "16:00")]
    grille = GrilleHoraire.depuis_configuration(
        ["Mercredi"], horaires,
        [("matin", [0, 1, 2, 3]), ("apres-midi", [4, 5, 6])])
    par_seance = {c.index_seance: c.id for c in grille.creneaux}

    salles = [Salle(1, "S1", 40)]
    classes = [Classe(1, "C1", effectif=30, salle_attitree_id=1,
                      max_heures_par_jour=7)]
    matieres = [Matiere(1, "Maths")]
    professeurs = [Professeur(1, "Ma", "T6", matieres_ids=[1])]
    cours = [CoursRequis(1, 1, 1, 1, heures_par_semaine=4)]

    lecons = [
        LeconPlanifiee(cours_requis_id=1, classe_id=1, matiere_id=1,
                       professeur_id=1, salle_id=1,
                       creneau_id=par_seance[position])
        for position in (0, 2, 4, 5)
    ]
    metriques = evaluer(lecons, grille, salles, matieres, professeurs,
                        classes, cours)

    # Par demi-journée, une seule séance creuse est visible (la 09:00).
    assert metriques.trous_professeurs == 1
    # Sur la journée entière, il y en a deux : 09:00 et 11:05.
    assert metriques.heures_creuses_journee == 2, metriques.heures_creuses_journee
    assert metriques.journees_hachees_professeurs == 1
    assert metriques.heures_creuses_en_trop == 1


def test_heures_creuses_reparties_sur_des_jours_differents():
    """
    Deux heures creuses sont inévitables. Le poids doit les répartir sur
    deux journées plutôt que de les concentrer sur une seule : à nombre
    d'heures creuses égal, un enseignant préfère une heure perdue deux
    jours qu'un après-midi entier troué le même jour.

    Le mardi est fermé après la troisième séance, ce qui rend les deux
    journées dissymétriques et laisse un vrai choix au solveur.
    """
    horaires = [(f"{8 + i:02d}:00", f"{8 + i:02d}:55") for i in range(4)]
    grille = GrilleHoraire.depuis_configuration(
        ["Lundi", "Mardi"], horaires, [("journee", list(range(4)))],
        fermetures=[(1, [3])])
    creneau = {(c.jour, c.index_seance): c.id for c in grille.creneaux}
    tous = {c.id for c in grille.creneaux}

    salles = [Salle(i + 1, f"S{i + 1}", 40) for i in range(5)]
    classes = [Classe(i + 1, f"C{i + 1}", effectif=30,
                      salle_attitree_id=i + 1, max_heures_par_jour=4)
               for i in range(5)]
    matieres = [Matiere(1, "Maths")]
    prof = Professeur(1, "Unique", "Prof", matieres_ids=[1],
                      max_heures_consecutives=4, max_heures_par_jour=4)

    # Quatre cours épinglés aux extrémités des deux journées, un libre.
    epingles = [("Lundi", 0), ("Lundi", 3), ("Mardi", 0), ("Mardi", 2)]
    cours = [
        CoursRequis(i + 1, i + 1, 1, 1, heures_par_semaine=1,
                    max_heures_par_jour=1,
                    creneaux_interdits=tous - {creneau[cle]})
        for i, cle in enumerate(epingles)
    ]
    cours.append(CoursRequis(5, 5, 1, 1, heures_par_semaine=1,
                             max_heures_par_jour=1))

    ponderations = Ponderations(
        trous_professeurs=6, trous_doubles_professeurs=0,
        heure_isolee_professeur=0, jours_presence_professeurs=0,
        recompense_permanence=0, penalites_seance={},
        equite_derniere_seance=0, equilibrage_charge_classes=0,
        demi_journees_travaillees_classes=0,
        journee_hachee_professeur=40)

    resultat = SolveurEmploiDuTemps(
        grille=grille, salles=salles, matieres=matieres, professeurs=[prof],
        classes=classes, cours_requis=cours,
        options=Options(limite_secondes=25, zero_trou_classes=False),
        ponderations=ponderations).resoudre()
    assert resultat.reussi, resultat.statut

    metriques = evaluer(resultat.lecons, grille, salles, matieres, [prof],
                        classes, cours)
    # Deux heures creuses au total, mais jamais deux le même jour.
    assert metriques.trous_professeurs == 2, metriques.trous_professeurs
    assert metriques.journees_hachees_professeurs == 0
    assert metriques.heures_creuses_en_trop == 0


def test_metrique_compte_les_charges_quotidiennes():
    """
    Un enseignant présent cinq heures lundi et deux heures mardi : la
    métrique décrit la distribution, une journée par entrée.
    """
    horaires = [(f"{8 + i:02d}:00", f"{8 + i:02d}:55") for i in range(5)]
    grille = GrilleHoraire.depuis_configuration(
        ["Lundi", "Mardi"], horaires, [("journee", list(range(5)))])
    creneau = {(c.jour, c.index_seance): c.id for c in grille.creneaux}

    salles = [Salle(1, "S1", 40)]
    classes = [Classe(1, "C1", effectif=30, salle_attitree_id=1)]
    matieres = [Matiere(1, "Maths")]
    professeurs = [Professeur(1, "Unique", "Prof", matieres_ids=[1])]
    cours = [CoursRequis(1, 1, 1, 1, heures_par_semaine=7)]

    places = [("Lundi", i) for i in range(5)] + [("Mardi", i) for i in range(2)]
    lecons = [
        LeconPlanifiee(cours_requis_id=1, classe_id=1, matiere_id=1,
                       professeur_id=1, salle_id=1,
                       creneau_id=creneau[cle])
        for cle in places
    ]
    metriques = evaluer(lecons, grille, salles, matieres, professeurs,
                        classes, cours)
    assert metriques.charges_quotidiennes_professeurs == {2: 1, 5: 1}


def test_penalite_de_charge_repartit_les_heures_sur_deux_journees():
    """
    Six heures à placer pour un seul enseignant sur deux journées de six
    séances. Le poids des jours de présence pousse à tout concentrer sur
    le lundi ; les seuils de charge quotidienne, qui se cumulent, doivent
    l'emporter et étaler la semaine.
    """
    horaires = [(f"{8 + i:02d}:00", f"{8 + i:02d}:55") for i in range(6)]
    grille = GrilleHoraire.depuis_configuration(
        ["Lundi", "Mardi"], horaires, [("journee", list(range(6)))])

    salles = [Salle(i + 1, f"S{i + 1}", 40) for i in range(6)]
    classes = [Classe(i + 1, f"C{i + 1}", effectif=30, salle_attitree_id=i + 1)
               for i in range(6)]
    matieres = [Matiere(1, "Maths")]
    prof = Professeur(1, "Unique", "Prof", matieres_ids=[1],
                      max_heures_consecutives=6, max_heures_par_jour=6)
    cours = [CoursRequis(i + 1, i + 1, 1, 1, heures_par_semaine=1)
             for i in range(6)]

    reglages = dict(
        trous_professeurs=0, trous_doubles_professeurs=0,
        journee_hachee_professeur=0, heure_isolee_professeur=0,
        recompense_permanence=0, penalites_seance={},
        equite_derniere_seance=0, equilibrage_charge_classes=0,
        demi_journees_travaillees_classes=0,
        jours_presence_professeurs=10)

    def charges(penalites):
        resultat = SolveurEmploiDuTemps(
            grille=grille, salles=salles, matieres=matieres,
            professeurs=[prof], classes=classes, cours_requis=cours,
            options=Options(limite_secondes=25, zero_trou_classes=False),
            ponderations=Ponderations(
                penalites_heures_par_jour=penalites, **reglages)).resoudre()
        assert resultat.reussi, resultat.statut
        return evaluer(resultat.lecons, grille, salles, matieres, [prof],
                       classes, cours).charges_quotidiennes_professeurs

    # Sans les seuils, la journée unique de six heures est optimale.
    assert charges({}) == {6: 1}
    # Avec eux, l'enseignant vient deux jours et ne dépasse jamais quatre
    # heures : le seuil de cinq heures n'est plus atteint.
    reparti = charges({5: 15, 6: 45})
    assert sum(n * j for n, j in reparti.items()) == 6, reparti
    assert max(reparti) <= 4, reparti


def _classe_a_deux_services():
    """
    Une division de 8 h sur deux journées de quatre séances.

    Deux matières à bloc de 2 h (A et B) et deux matières en heures
    isolées (C et D), chacune portée par DEUX services d'une heure —
    la configuration réelle d'un cours doublé d'un TD dédoublé. Le
    plafond journalier D9 ne voit que le service : rien ne l'empêche de
    poser les deux heures de C le même jour.

    Le professeur de C assure ses deux services : les grouper lui
    économise une journée de présence, ce qui rend l'empilement
    attirant tant que le nouveau critère est à zéro.
    """
    horaires = [(f"{8 + i:02d}:00", f"{8 + i:02d}:55") for i in range(4)]
    grille = GrilleHoraire.depuis_configuration(
        ["Lundi", "Mardi"], horaires, [("journee", list(range(4)))])

    salles = [Salle(1, "S1", 40)]
    classes = [Classe(1, "C1", effectif=30, salle_attitree_id=1,
                      max_heures_par_jour=4)]
    matieres = [Matiere(i, f"M{i}") for i in (1, 2, 3, 4)]
    professeurs = [
        Professeur(i, f"P{i}", "Prof", matieres_ids=[i],
                   max_heures_consecutives=4, max_heures_par_jour=4)
        for i in (1, 2, 3, 4)
    ]
    cours = [
        # A et B : un bloc de 2 h chacune, une journée doublée permise.
        CoursRequis(1, 1, 1, 1, heures_par_semaine=2, nb_seances_doubles=1,
                    max_heures_par_jour=2),
        CoursRequis(2, 1, 2, 2, heures_par_semaine=2, nb_seances_doubles=1,
                    max_heures_par_jour=2),
        # C et D : deux services d'une heure, aucun bloc autorisé.
        CoursRequis(3, 1, 3, 3, heures_par_semaine=1, max_heures_par_jour=1),
        CoursRequis(4, 1, 3, 3, heures_par_semaine=1, max_heures_par_jour=1),
        CoursRequis(5, 1, 4, 4, heures_par_semaine=1, max_heures_par_jour=1),
        CoursRequis(6, 1, 4, 4, heures_par_semaine=1, max_heures_par_jour=1),
    ]
    return grille, salles, classes, matieres, professeurs, cours


def _resoudre_deux_services(**poids):
    grille, salles, classes, matieres, professeurs, cours = \
        _classe_a_deux_services()
    reglages = dict(
        trous_professeurs=0, trous_doubles_professeurs=0,
        journee_hachee_professeur=0, heure_isolee_professeur=0,
        recompense_permanence=0, penalites_seance={},
        penalites_heures_par_jour={}, equite_derniere_seance=0,
        equilibrage_charge_classes=0, demi_journees_travaillees_classes=0,
        blocs_hors_politique=0, matieres_repetees_par_jour=0,
        # Grouper les heures de C et de D économise une journée de
        # présence : sans le nouveau critère, l'empilement l'emporte.
        jours_presence_professeurs=20)
    reglages.update(poids)
    resultat = SolveurEmploiDuTemps(
        grille=grille, salles=salles, matieres=matieres,
        professeurs=professeurs, classes=classes, cours_requis=cours,
        options=Options(limite_secondes=20),
        ponderations=Ponderations(**reglages)).resoudre()
    assert resultat.reussi, resultat.statut
    return evaluer(resultat.lecons, grille, salles, matieres, professeurs,
                   classes, cours)


def test_heures_groupees_au_dela_de_la_politique_sont_penalisees():
    """
    C et D n'ont droit à aucun bloc : leurs deux heures doivent tomber
    sur des journées différentes. Le plafond journalier ne peut pas
    l'imposer, puisqu'il raisonne service par service.
    """
    sans = _resoudre_deux_services()
    assert sans.blocs_hors_politique == 2, sans.blocs_hors_politique

    avec = _resoudre_deux_services(blocs_hors_politique=30)
    assert avec.blocs_hors_politique == 0, avec.blocs_hors_politique


def test_empilement_de_matieres_doublees_est_penalise():
    """
    Une journée porte normalement un seul bloc de 2 h. Sans le critère,
    la division récolte deux matières doublées le même jour.
    """
    sans = _resoudre_deux_services()
    assert sans.empilements_de_matieres == 2, sans.empilements_de_matieres

    avec = _resoudre_deux_services(matieres_repetees_par_jour=30)
    assert avec.empilements_de_matieres == 0, avec.empilements_de_matieres
    assert avec.matieres_doublees_par_jour == {1: 2}, \
        avec.matieres_doublees_par_jour


def test_fouj_ne_compte_pas_pour_deux_matieres_doublees():
    """
    Pendant un fouj, G1 fait de la physique et G2 des sciences
    naturelles sur le même créneau. Aucun élève ne suit les deux : la
    division ne porte pas là deux matières doublées, elle en porte une
    par demi-groupe.
    """
    horaires = [(f"{8 + i:02d}:00", f"{8 + i:02d}:55") for i in range(4)]
    grille = GrilleHoraire.depuis_configuration(
        ["Lundi"], horaires, [("journee", list(range(4)))])
    par_seance = {c.index_seance: c.id for c in grille.creneaux}

    salles = [Salle(1, "S1", 40), Salle(2, "Labo", 40)]
    classes = [Classe(1, "C1", effectif=30, salle_attitree_id=1)]
    matieres = [Matiere(1, "Physique"), Matiere(2, "Sciences"),
                Matiere(3, "Maths")]
    professeurs = [Professeur(i, f"P{i}", "Prof", matieres_ids=[i])
                   for i in (1, 2, 3)]
    cours = [
        CoursRequis(1, 1, 1, 1, heures_par_semaine=2, nb_seances_doubles=1,
                    max_heures_par_jour=2, couplage_id="F1", groupe="G1"),
        CoursRequis(2, 1, 2, 2, heures_par_semaine=2, nb_seances_doubles=1,
                    max_heures_par_jour=2, couplage_id="F1", groupe="G2"),
        CoursRequis(3, 1, 3, 3, heures_par_semaine=2, nb_seances_doubles=1,
                    max_heures_par_jour=2),
    ]

    def lecon(cours_id, matiere_id, prof_id, salle_id, seance):
        return LeconPlanifiee(
            cours_requis_id=cours_id, classe_id=1, matiere_id=matiere_id,
            professeur_id=prof_id, salle_id=salle_id,
            creneau_id=par_seance[seance])

    # Le fouj occupe les deux premières séances, les maths les deux
    # suivantes.
    lecons = [lecon(1, 1, 1, 1, s) for s in (0, 1)]
    lecons += [lecon(2, 2, 2, 2, s) for s in (0, 1)]
    lecons += [lecon(3, 3, 3, 1, s) for s in (2, 3)]

    metriques = evaluer(lecons, grille, salles, matieres, professeurs,
                        classes, cours)
    # Chaque demi-groupe voit deux matières doublées : la sienne pendant
    # le fouj, et les maths. Un empilement par demi-groupe, pas quatre
    # matières entassées sur la division.
    assert metriques.matieres_doublees_par_jour == {2: 2}, \
        metriques.matieres_doublees_par_jour
    assert metriques.empilements_de_matieres == 2
    # Un bloc est prévu pour chacune des trois matières : rien hors
    # politique, et aucune matière à trois heures.
    assert metriques.blocs_hors_politique == 0
    assert metriques.matieres_a_trois_heures == 0


def test_politique_de_blocs_se_decline():
    """
    Le programme dit comment répartir les heures entre les journées.
    La forme « ONE_2H_BLOCK_REST_1H » se décline, et les fichiers
    d'établissement en écrivent des variantes.
    """
    from donnees.cem20 import blocs_de_la_politique as blocs

    assert blocs("") == 0
    assert blocs("NONE") == 0
    assert blocs("SINGLE_HOURS") == 0
    assert blocs("ONE_2H_BLOCK_REST_1H") == 1
    assert blocs("TWO_2H_HOURS_BLOCK_REST_1H") == 2
    assert blocs("THREE_2H_BLOCKS_REST_1H") == 3
    assert blocs("2_2H_BLOCK_REST_1H") == 2
    try:
        blocs("DEUX_BLOCS")
    except ValueError as erreur:
        assert "politique de blocs inconnue" in str(erreur)
    else:
        raise AssertionError("une politique illisible doit être refusée")


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
