"""
Jeu de données de référence : CEM « Ibn Khaldoun » — Alger.

Établissement complet et réaliste servant de banc d'essai :
12 divisions (3 par niveau, de la 1ʳᵉ à la 4ᵉ année moyenne),
23 enseignants, 348 heures à placer par semaine.

Ce fichier sera remplacé par les données réelles du CEM fourni ;
il définit en attendant la structure attendue.
"""

from typing import Dict, List, Tuple

from solver.models import (
    Classe, CoursRequis, GrilleHoraire, JOURS_SEMAINE_DZ, Matiere,
    Options, Ponderations, Professeur, Salle,
)

# ══════════════════════════════════════════════════════════════════
#  GRILLE HORAIRE
#  Dimanche → Jeudi ; 4 séances le matin, 3 l'après-midi.
# ══════════════════════════════════════════════════════════════════

grille = GrilleHoraire.construire(
    jours=JOURS_SEMAINE_DZ,
    seances_matin=[("08:00", "08:55"), ("09:00", "09:55"),
                   ("10:05", "11:00"), ("11:05", "12:00")],
    seances_apres_midi=[("13:00", "13:55"), ("14:00", "14:55"),
                        ("15:05", "16:00")],
)
creneaux = grille.creneaux   # 5 jours × 7 séances = 35 créneaux

# ══════════════════════════════════════════════════════════════════
#  MATIÈRES
# ══════════════════════════════════════════════════════════════════

M_ARABE, M_MATHS, M_FRANCAIS, M_ANGLAIS = 1, 2, 3, 4
M_PHYSIQUE, M_SVT, M_HISTGEO, M_ISLAM = 5, 6, 7, 8
M_CIVIQUE, M_INFO, M_EPS, M_ARTS = 9, 10, 11, 12

matieres = [
    Matiere(M_ARABE,    "Langue Arabe",        5.0, prefere_matin=True),
    Matiere(M_MATHS,    "Mathématiques",       4.0, prefere_matin=True),
    Matiere(M_FRANCAIS, "Langue Française",    3.0, prefere_matin=True),
    Matiere(M_ANGLAIS,  "Langue Anglaise",     2.0),
    Matiere(M_PHYSIQUE, "Sciences Physiques",  2.0, type_salle_requis="labo",
            prefere_matin=True),
    Matiere(M_SVT,      "Sciences Naturelles", 2.0, type_salle_requis="labo"),
    Matiere(M_HISTGEO,  "Histoire-Géographie", 2.0),
    Matiere(M_ISLAM,    "Éducation Islamique", 2.0),
    Matiere(M_CIVIQUE,  "Éducation Civique",   1.0),
    Matiere(M_INFO,     "Informatique",        1.0, type_salle_requis="info"),
    Matiere(M_EPS,      "Éducation Physique",  1.0, type_salle_requis="sport"),
    Matiere(M_ARTS,     "Éducation Artistique", 1.0),
]

# ══════════════════════════════════════════════════════════════════
#  SALLES
#  Une salle de classe attitrée par division + salles spécialisées.
# ══════════════════════════════════════════════════════════════════

salles: List[Salle] = []
for i in range(12):
    salles.append(Salle(id=i + 1, nom=f"Salle {101 + i}", capacite=40))
salles += [
    Salle(id=21, nom="Labo Sciences 1", capacite=36, type="labo"),
    Salle(id=22, nom="Labo Sciences 2", capacite=36, type="labo"),
    Salle(id=23, nom="Salle Informatique", capacite=36, type="info"),
    Salle(id=24, nom="Terrain de sport", capacite=40, type="sport"),
    Salle(id=25, nom="Salle omnisports", capacite=40, type="sport"),
]

# ══════════════════════════════════════════════════════════════════
#  CLASSES — 3 divisions par niveau, salle attitrée
# ══════════════════════════════════════════════════════════════════

NIVEAUX = ["1AM", "2AM", "3AM", "4AM"]
EFFECTIFS = {"1AM": 36, "2AM": 35, "3AM": 34, "4AM": 32}

classes: List[Classe] = []
classe_id = 1
for niveau in NIVEAUX:
    for section in ("A", "B", "C"):
        classes.append(Classe(
            id=classe_id,
            nom=f"{niveau} {section}",
            niveau=niveau,
            effectif=EFFECTIFS[niveau],
            salle_attitree_id=classe_id,   # Salle 101 → 112
            max_heures_par_jour=6,
        ))
        classe_id += 1

# ══════════════════════════════════════════════════════════════════
#  PROGRAMME OFFICIEL — volume hebdomadaire par niveau
#  (matiere_id, heures/semaine, nb séances doubles, max h/jour)
# ══════════════════════════════════════════════════════════════════

PROGRAMME: Dict[str, List[Tuple[int, int, int, int]]] = {
    "1AM": [(M_ARABE, 5, 1, 2), (M_MATHS, 4, 1, 2), (M_FRANCAIS, 4, 1, 2),
            (M_ANGLAIS, 3, 0, 1), (M_PHYSIQUE, 2, 0, 1), (M_SVT, 2, 0, 1),
            (M_HISTGEO, 2, 0, 1), (M_ISLAM, 1, 0, 1), (M_CIVIQUE, 1, 0, 1),
            (M_INFO, 1, 0, 1), (M_EPS, 2, 1, 2), (M_ARTS, 1, 0, 1)],
    "2AM": [(M_ARABE, 5, 1, 2), (M_MATHS, 4, 1, 2), (M_FRANCAIS, 4, 1, 2),
            (M_ANGLAIS, 3, 0, 1), (M_PHYSIQUE, 2, 0, 1), (M_SVT, 2, 0, 1),
            (M_HISTGEO, 2, 0, 1), (M_ISLAM, 1, 0, 1), (M_CIVIQUE, 1, 0, 1),
            (M_INFO, 1, 0, 1), (M_EPS, 2, 1, 2), (M_ARTS, 1, 0, 1)],
    "3AM": [(M_ARABE, 5, 1, 2), (M_MATHS, 5, 1, 2), (M_FRANCAIS, 4, 1, 2),
            (M_ANGLAIS, 3, 0, 1), (M_PHYSIQUE, 2, 0, 1), (M_SVT, 2, 0, 1),
            (M_HISTGEO, 2, 0, 1), (M_ISLAM, 1, 0, 1), (M_CIVIQUE, 1, 0, 1),
            (M_INFO, 1, 0, 1), (M_EPS, 2, 1, 2), (M_ARTS, 1, 0, 1)],
    "4AM": [(M_ARABE, 5, 1, 2), (M_MATHS, 5, 1, 2), (M_FRANCAIS, 4, 1, 2),
            (M_ANGLAIS, 3, 0, 1), (M_PHYSIQUE, 2, 0, 1), (M_SVT, 2, 0, 1),
            (M_HISTGEO, 2, 0, 1), (M_ISLAM, 1, 0, 1), (M_CIVIQUE, 1, 0, 1),
            (M_INFO, 1, 0, 1), (M_EPS, 2, 1, 2), (M_ARTS, 1, 0, 1)],
}

# ══════════════════════════════════════════════════════════════════
#  PROFESSEURS — dimensionnés sur le volume réel de chaque matière
# ══════════════════════════════════════════════════════════════════

NOMS = [
    ("Benali", "Karim"), ("Meziane", "Fatima"), ("Hadj", "Amina"),
    ("Bouzid", "Mohamed"), ("Kaci", "Leila"), ("Rouag", "Sofiane"),
    ("Saadi", "Nadia"), ("Mansouri", "Omar"), ("Cherif", "Yasmine"),
    ("Belkacem", "Rachid"), ("Zerrouki", "Samira"), ("Ait Ali", "Hocine"),
    ("Boudjema", "Nawel"), ("Lounis", "Farid"), ("Hamidi", "Souad"),
    ("Terki", "Djamel"), ("Ould Ali", "Malika"), ("Brahimi", "Youcef"),
    ("Guerrouj", "Assia"), ("Slimani", "Tarek"), ("Ferhat", "Lynda"),
    ("Chaoui", "Bilal"), ("Nait Kaci", "Zohra"),
]

# Nombre d'enseignants par matière (couvre la charge des 12 divisions).
EFFECTIF_CORPS = {
    M_ARABE: 3, M_MATHS: 3, M_FRANCAIS: 3, M_ANGLAIS: 2,
    M_PHYSIQUE: 2, M_SVT: 2, M_HISTGEO: 2, M_ISLAM: 1,
    M_CIVIQUE: 1, M_INFO: 1, M_EPS: 2, M_ARTS: 1,
}

professeurs: List[Professeur] = []
corps: Dict[int, List[int]] = {}
_prof_id = 1
for matiere_id, nombre in EFFECTIF_CORPS.items():
    corps[matiere_id] = []
    for _ in range(nombre):
        nom, prenom = NOMS[(_prof_id - 1) % len(NOMS)]
        professeurs.append(Professeur(
            id=_prof_id, nom=nom, prenom=prenom,
            matieres_ids=[matiere_id],
            max_heures_consecutives=4,
            max_heures_par_jour=6,
        ))
        corps[matiere_id].append(_prof_id)
        _prof_id += 1

# Contraintes individuelles : deux enseignants partagés avec un autre
# établissement ne sont présents que trois jours par semaine.
_indisponible_jeudi = {c.id for c in creneaux if c.jour == "Jeudi"}
_tous = {c.id for c in creneaux}
professeurs[corps[M_INFO][0] - 1].creneaux_disponibles = _tous - _indisponible_jeudi
professeurs[corps[M_ARTS][0] - 1].creneaux_disponibles = _tous - _indisponible_jeudi
# Une enseignante regroupe son service sur quatre jours.
professeurs[corps[M_HISTGEO][0] - 1].max_jours_presence = 4

# ══════════════════════════════════════════════════════════════════
#  COURS REQUIS — croisement classes × programme
# ══════════════════════════════════════════════════════════════════

cours_requis: List[CoursRequis] = []
_cours_id = 1
_rotation: Dict[int, int] = {m: 0 for m in EFFECTIF_CORPS}

for classe in classes:
    for matiere_id, heures, doubles, max_jour in PROGRAMME[classe.niveau]:
        enseignants = corps[matiere_id]
        prof_id = enseignants[_rotation[matiere_id] % len(enseignants)]
        _rotation[matiere_id] += 1
        cours_requis.append(CoursRequis(
            id=_cours_id,
            classe_id=classe.id,
            matiere_id=matiere_id,
            professeur_id=prof_id,
            heures_par_semaine=heures,
            nb_seances_doubles=doubles,
            max_heures_par_jour=max_jour,
        ))
        _cours_id += 1

# ══════════════════════════════════════════════════════════════════
#  PARAMÉTRAGE PAR DÉFAUT
# ══════════════════════════════════════════════════════════════════

options = Options(limite_secondes=120)
ponderations = Ponderations()
