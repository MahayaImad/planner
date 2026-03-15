"""
Données de test : École privée fictive "Ibn Khaldoun" — Alger
Niveau : Collège (CEM) — 3 classes de 4ème année moyenne

Semaine algérienne : Samedi → Jeudi (Vendredi = repos)
Horaires : 8h00 → 17h00, créneaux de 1h, pause déjeuner 12h-13h
"""

from solver.models import (
    Creneau, Salle, Matiere, Professeur,
    Classe, CoursRequis
)


# ─────────────────────────────────────────────
# CRÉNEAUX HORAIRES
# Samedi → Jeudi, 8h-12h et 13h-17h (4h matin + 4h après-midi = 8h/jour)
# ─────────────────────────────────────────────

JOURS = ["Samedi", "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]
HEURES = [
    ("08:00", "09:00"),
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    # 12h-13h : pause déjeuner (pas de créneau)
    ("13:00", "14:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
    ("16:00", "17:00"),
]

creneaux = []
creneau_id = 1
for jour in JOURS:
    for heure_debut, heure_fin in HEURES:
        creneaux.append(Creneau(
            id=creneau_id,
            jour=jour,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
        ))
        creneau_id += 1

# Total : 6 jours × 8 créneaux = 48 créneaux/semaine


# ─────────────────────────────────────────────
# SALLES
# ─────────────────────────────────────────────

salles = [
    Salle(id=1, nom="Salle 101", capacite=35, type="classique"),
    Salle(id=2, nom="Salle 102", capacite=35, type="classique"),
    Salle(id=3, nom="Salle 103", capacite=35, type="classique"),
    Salle(id=4, nom="Labo Sciences", capacite=30, type="labo"),
    Salle(id=5, nom="Salle Info", capacite=25, type="info"),
]


# ─────────────────────────────────────────────
# MATIÈRES
# Programme 4ème année moyenne (Algérie)
# ─────────────────────────────────────────────

matieres = [
    Matiere(id=1,  nom="Mathématiques",         coefficient=4.0),
    Matiere(id=2,  nom="Physique-Chimie",        coefficient=3.0),
    Matiere(id=3,  nom="Sciences Naturelles",    coefficient=2.0),
    Matiere(id=4,  nom="Langue Arabe",           coefficient=5.0),
    Matiere(id=5,  nom="Langue Française",       coefficient=4.0),
    Matiere(id=6,  nom="Langue Anglaise",        coefficient=3.0),
    Matiere(id=7,  nom="Histoire-Géographie",    coefficient=2.0),
    Matiere(id=8,  nom="Éducation Islamique",    coefficient=2.0),
    Matiere(id=9,  nom="Éducation Civique",      coefficient=1.0),
    Matiere(id=10, nom="Informatique",           coefficient=1.0),
]


# ─────────────────────────────────────────────
# PROFESSEURS
# Chaque prof enseigne 1 ou 2 matières
# Disponibilités : vide = disponible tout le temps
# ─────────────────────────────────────────────

# Créneaux du Jeudi après-midi indisponibles pour certains profs
# (réunion pédagogique Jeudi 15h-17h = créneaux 47 et 48)
JEUDI_PM = {47, 48}

professeurs = [
    Professeur(
        id=1, nom="Benali", prenom="Karim",
        matieres_ids=[1],  # Maths
        max_heures_consecutives=3,
    ),
    Professeur(
        id=2, nom="Meziane", prenom="Fatima",
        matieres_ids=[2],  # Physique-Chimie
        max_heures_consecutives=3,
    ),
    Professeur(
        id=3, nom="Hadj", prenom="Amina",
        matieres_ids=[3],  # Sciences Nat → labo
        max_heures_consecutives=2,
    ),
    Professeur(
        id=4, nom="Bouzid", prenom="Mohamed",
        matieres_ids=[4],  # Arabe
        max_heures_consecutives=4,
    ),
    Professeur(
        id=5, nom="Kaci", prenom="Leila",
        matieres_ids=[5],  # Français
        max_heures_consecutives=3,
    ),
    Professeur(
        id=6, nom="Rouag", prenom="Sofiane",
        matieres_ids=[6],  # Anglais
        max_heures_consecutives=3,
        creneaux_disponibles=set(range(1, 49)) - JEUDI_PM,
    ),
    Professeur(
        id=7, nom="Saadi", prenom="Nadia",
        matieres_ids=[7],  # Histoire-Géo
        max_heures_consecutives=3,
    ),
    Professeur(
        id=8, nom="Mansouri", prenom="Omar",
        matieres_ids=[8, 9],  # Éducation Islamique + Civique
        max_heures_consecutives=3,
    ),
    Professeur(
        id=9, nom="Cherif", prenom="Yasmine",
        matieres_ids=[10],  # Informatique → salle info
        max_heures_consecutives=2,
        creneaux_disponibles=set(range(1, 49)) - JEUDI_PM,
    ),
]


# ─────────────────────────────────────────────
# CLASSES
# 3 sections de 4ème année moyenne
# ─────────────────────────────────────────────

classes = [
    Classe(id=1, nom="4ème A", niveau="moyen", effectif=32),
    Classe(id=2, nom="4ème B", niveau="moyen", effectif=30),
    Classe(id=3, nom="4ème C", niveau="moyen", effectif=28),
]


# ─────────────────────────────────────────────
# COURS REQUIS
# Volume horaire hebdomadaire par classe
# (programme officiel algérien 4ème moyenne, simplifié)
# ─────────────────────────────────────────────
#
# Maths:        5h  | Physique:  3h | Sciences: 2h
# Arabe:        5h  | Français:  4h | Anglais:  3h
# Hist-Géo:     2h  | Isl+Civ:  2h | Info:     1h
# Total/classe: 27h/semaine (sur 48 créneaux dispo)

def generer_cours_requis(classes, matieres_ids_volumes, debut_id=1):
    """
    matieres_ids_volumes : liste de (matiere_id, prof_id, heures, type_salle)
    """
    cours = []
    cid = debut_id
    for classe in classes:
        for matiere_id, prof_id, heures, type_salle in matieres_ids_volumes:
            cours.append(CoursRequis(
                id=cid,
                classe_id=classe.id,
                matiere_id=matiere_id,
                professeur_id=prof_id,
                heures_par_semaine=heures,
                type_salle_requis=type_salle,
            ))
            cid += 1
    return cours


PROGRAMME = [
    # (matiere_id, prof_id, heures/semaine, type_salle)
    (1,  1, 5, None),       # Maths       → Benali        → salle classique
    (2,  2, 3, None),       # Physique    → Meziane       → salle classique
    (3,  3, 2, "labo"),     # Sciences    → Hadj          → labo
    (4,  4, 5, None),       # Arabe       → Bouzid        → salle classique
    (5,  5, 4, None),       # Français    → Kaci          → salle classique
    (6,  6, 3, None),       # Anglais     → Rouag         → salle classique
    (7,  7, 2, None),       # Hist-Géo    → Saadi         → salle classique
    (8,  8, 1, None),       # Éd. Islam.  → Mansouri      → salle classique
    (9,  8, 1, None),       # Éd. Civique → Mansouri      → salle classique
    (10, 9, 1, "info"),     # Informatique→ Cherif        → salle info
]
# Total par classe : 5+3+2+5+4+3+2+1+1+1 = 27 heures/semaine

cours_requis = generer_cours_requis(classes, PROGRAMME)
