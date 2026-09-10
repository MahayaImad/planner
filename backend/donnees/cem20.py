"""
CEM algérien à 20 divisions — ALGERIAN_CEM_20CLASSES.

Encodage direct des fichiers fournis par l'établissement : grille
horaire, divisions, salles, programme officiel, fenêtres pédagogiques
et règles de dédoublement (fouj). Les tableaux sont conservés dans leur
format d'origine et analysés ici, ce qui donne le chemin d'import que
la plateforme suivra.

⚠ Le corps enseignant n'a pas été fourni : il est reconstitué ci-dessous
à partir du volume horaire de chaque matière (49 enseignants). C'est la
seule partie fictive du jeu de données.
"""

import csv
import io
import os
from collections import defaultdict
from typing import Dict, List

from solver.models import (
    Classe, CoursRequis, FenetrePedagogique, GrilleHoraire, Matiere,
    Options, Ponderations, Professeur, Salle,
)

# ══════════════════════════════════════════════════════════════════
#  GRILLE HORAIRE — school_grid
# ══════════════════════════════════════════════════════════════════

JOURS = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]

HORAIRES = [
    ("08:00", "08:55"),   # séance 0
    ("09:00", "09:55"),   # séance 1
    ("10:05", "11:00"),   # séance 2
    ("11:05", "12:00"),   # séance 3   ← fin du matin (lunch_boundary_slot)
    ("13:00", "13:55"),   # séance 4
    ("14:00", "14:55"),   # séance 5
    ("15:05", "16:00"),   # séance 6
]

SHIFTS = [("matin", [0, 1, 2, 3]), ("apres-midi", [4, 5, 6])]

# Mardi après-midi fermé (règle officielle du CEM).
FERMETURES = [(2, [4, 5, 6])]

grille = GrilleHoraire.depuis_configuration(JOURS, HORAIRES, SHIFTS, FERMETURES)
creneaux = grille.creneaux          # 5 × 7 − 3 = 32 créneaux ouverts

# ══════════════════════════════════════════════════════════════════
#  MATIÈRES
# ══════════════════════════════════════════════════════════════════

# Le tamazight a été retiré du programme sur décision de
# l'établissement : les fiches enseignants fournies ne comportaient
# aucun professeur qualifié pour les 60 h hebdomadaires qu'il exigeait.
# Pour le rétablir : remettre sa ligne ici et les quatre lignes de
# niveau dans CURRICULUM_CSV, puis déclarer les enseignants
# correspondants dans STAFF_CSV.
MATIERES_CSV = """\
code,nom
ARABIC,اللغة العربية — Langue arabe
FRENCH,اللغة الفرنسية — Français
ENGLISH,اللغة الإنجليزية — Anglais
MATH,رياضيات — Mathématiques
SCIENCE,العلوم الطبيعية — Sciences naturelles
PHYS,العلوم الفيزيائية — Sciences physiques
HIST,التاريخ — Histoire
GEO,الجغرافيا — Géographie
ISLAMIC,التربية الإسلامية — Éducation islamique
CIVICS,تربية مدنية — Éducation civique
ART_MUSIC,التربية التشكيلية — Éducation artistique
PE,التربية البدنية — Éducation physique
INFO,الإعلام الآلي — Informatique
"""

matieres: List[Matiere] = []
ID_MATIERE: Dict[str, int] = {}
for i, ligne in enumerate(csv.DictReader(io.StringIO(MATIERES_CSV)), start=1):
    ID_MATIERE[ligne["code"]] = i
    matieres.append(Matiere(id=i, nom=ligne["nom"]))

# ══════════════════════════════════════════════════════════════════
#  SALLES — la colonne « Capacity » est un NOMBRE DE SALLES
# ══════════════════════════════════════════════════════════════════

# Nom du type de salle ordinaire dans le parc : tout autre type est
# une spécialité que seules les matières concernées mobilisent.
TYPE_SALLE_ORDINAIRE = "classroom"

PARC_SALLES = [
    ("classroom",   20, "R{:02d}",  "Salle {}"),
    ("lab_physics",  4, "LP{}",     "Labo Physique {}"),
    ("lab_bio",      4, "LB{}",     "Labo SVT {}"),
    ("it_room",      2, "IT{}",     "Salle Informatique {}"),
    ("field",        2, "TR{}",     "Terrain {}"),
]

salles: List[Salle] = []
ID_SALLE: Dict[str, int] = {}
_sid = 1
for type_salle, nombre, gabarit_code, gabarit_nom in PARC_SALLES:
    for n in range(1, nombre + 1):
        code = gabarit_code.format(n)
        ID_SALLE[code] = _sid
        # Aucune jauge de places n'a été fournie : capacité nominale.
        salles.append(Salle(id=_sid, nom=gabarit_nom.format(n),
                            capacite=40, type=type_salle))
        _sid += 1

# ══════════════════════════════════════════════════════════════════
#  DIVISIONS — classes.csv
# ══════════════════════════════════════════════════════════════════

CLASSES_CSV = """\
Class_ID,Level,Base_Room,Is_Mobile
1AM1,1AM,R01,FALSE
1AM2,1AM,R02,FALSE
1AM3,1AM,R03,FALSE
1AM4,1AM,R04,FALSE
1AM5,1AM,R05,FALSE
2AM1,2AM,R06,FALSE
2AM2,2AM,R07,FALSE
2AM3,2AM,R08,FALSE
2AM4,2AM,R09,FALSE
2AM5,2AM,R10,FALSE
3AM1,3AM,R11,FALSE
3AM2,3AM,R12,FALSE
3AM3,3AM,R13,FALSE
3AM4,3AM,R14,FALSE
3AM5,3AM,R15,FALSE
4AM1,4AM,R16,FALSE
4AM2,4AM,R17,FALSE
4AM3,4AM,R18,FALSE
4AM4,4AM,R19,FALSE
4AM5,4AM,R20,FALSE
"""

EFFECTIFS = {"1AM": 36, "2AM": 35, "3AM": 34, "4AM": 33}

classes: List[Classe] = []
ID_CLASSE: Dict[str, int] = {}
for i, ligne in enumerate(csv.DictReader(io.StringIO(CLASSES_CSV)), start=1):
    ID_CLASSE[ligne["Class_ID"]] = i
    classes.append(Classe(
        id=i,
        nom=ligne["Class_ID"],
        niveau=ligne["Level"],
        effectif=EFFECTIFS[ligne["Level"]],
        salle_attitree_id=(None if ligne["Is_Mobile"].strip().upper() == "TRUE"
                           else ID_SALLE[ligne["Base_Room"]]),
        max_heures_par_jour=len(HORAIRES),
    ))

# ══════════════════════════════════════════════════════════════════
#  PROGRAMME OFFICIEL — curriculum.csv
# ══════════════════════════════════════════════════════════════════

CURRICULUM_CSV = """\
Level,Subject_Code,Hrs_Cours,Cours_Block_Policy,Hrs_TD,TD_Delivery_Mode,Hrs_TP,TP_Delivery_Mode,Hrs_Practice,Practice_Block_Size,Required_Room_Type
1AM,ARABIC,5,ONE_2H_BLOCK_REST_1H,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
1AM,FRENCH,2,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
1AM,ENGLISH,3,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
1AM,MATH,4,ONE_2H_BLOCK_REST_1H,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
1AM,SCIENCE,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_bio
1AM,PHYS,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_physics
1AM,HIST,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
1AM,GEO,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
1AM,ISLAMIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
1AM,CIVICS,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
1AM,ART_MUSIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
1AM,PE,0,NONE,0,NONE,0,NONE,2,2,field
1AM,INFO,0,NONE,0,NONE,1,FORTNIGHTLY_30M,0,0,it_room
2AM,ARABIC,5,ONE_2H_BLOCK_REST_1H,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
2AM,FRENCH,2,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
2AM,ENGLISH,3,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
2AM,MATH,4,ONE_2H_BLOCK_REST_1H,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
2AM,SCIENCE,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_bio
2AM,PHYS,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_physics
2AM,HIST,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
2AM,GEO,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
2AM,ISLAMIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
2AM,CIVICS,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
2AM,ART_MUSIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
2AM,PE,0,NONE,0,NONE,0,NONE,2,2,field
2AM,INFO,0,NONE,0,NONE,1,FORTNIGHTLY_30M,0,0,it_room
3AM,ARABIC,4,ONE_2H_BLOCK_REST_1H,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
3AM,FRENCH,2,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
3AM,ENGLISH,3,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
3AM,MATH,4,ONE_2H_BLOCK_REST_1H,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
3AM,SCIENCE,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_bio
3AM,PHYS,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_physics
3AM,HIST,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
3AM,GEO,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
3AM,ISLAMIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
3AM,CIVICS,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
3AM,ART_MUSIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
3AM,PE,0,NONE,0,NONE,0,NONE,2,2,field
3AM,INFO,0,NONE,0,NONE,1,FORTNIGHTLY_30M,0,0,it_room
4AM,ARABIC,4,SINGLE_HOURS,2,WEEKLY_SWAP_2H,0,NONE,0,0,classroom
4AM,FRENCH,2,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
4AM,ENGLISH,3,SINGLE_HOURS,1,FORTNIGHTLY_30M,0,NONE,0,0,classroom
4AM,MATH,4,SINGLE_HOURS,2,WEEKLY_SWAP_2H,0,NONE,0,0,classroom
4AM,SCIENCE,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_bio
4AM,PHYS,1,SINGLE_HOURS,0,NONE,2,WEEKLY_SWAP_2H,0,0,lab_physics
4AM,HIST,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
4AM,GEO,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
4AM,ISLAMIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
4AM,CIVICS,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
4AM,ART_MUSIC,1,SINGLE_HOURS,0,NONE,0,NONE,0,0,classroom
4AM,PE,0,NONE,0,NONE,0,NONE,2,2,field
4AM,INFO,0,NONE,0,NONE,1,FORTNIGHTLY_30M,0,0,it_room
"""

PROGRAMME: Dict[str, Dict[str, dict]] = {}
for ligne in csv.DictReader(io.StringIO(CURRICULUM_CSV)):
    PROGRAMME.setdefault(ligne["Level"], {})[ligne["Subject_Code"]] = ligne

# ══════════════════════════════════════════════════════════════════
#  FENÊTRES PÉDAGOGIQUES — journées d'inspection
# ══════════════════════════════════════════════════════════════════

FENETRES_CSV = """\
Subject_Code,Day_Index,Blocked_Slots,Description
ARABIC,1,0;1;2;3,Inspection arabe — lundi matin
ISLAMIC,1,0;1;2;3,Inspection éducation islamique — lundi matin
FRENCH,2,0;1;2;3,Inspection français — mardi matin
ENGLISH,2,0;1;2;3,Inspection anglais — mardi matin
INFO,2,0;1;2;3,Inspection informatique — mardi matin
PHYS,3,0;1;2;3,Inspection physique — mercredi matin
SCIENCE,3,0;1;2;3,Inspection sciences naturelles — mercredi matin
MATH,4,0;1;2;3,Inspection mathématiques — jeudi matin
ART_MUSIC,4,0;1;2;3,Inspection éducation artistique — jeudi matin
HIST,0,0;1;2;3,Inspection histoire — dimanche matin
GEO,0,0;1;2;3,Inspection géographie — dimanche matin
CIVICS,0,0;1;2;3,Inspection éducation civique — dimanche matin
PE,0,0;1;2;3,Inspection éducation physique — dimanche matin
"""

fenetres_pedagogiques: List[FenetrePedagogique] = []
for ligne in csv.DictReader(io.StringIO(FENETRES_CSV)):
    fenetres_pedagogiques.append(FenetrePedagogique(
        matiere_id=ID_MATIERE[ligne["Subject_Code"]],
        index_jour=int(ligne["Day_Index"]),
        seances_bloquees={int(s) for s in ligne["Blocked_Slots"].split(";")},
        libelle=ligne["Description"],
    ))

# ══════════════════════════════════════════════════════════════════
#  RÈGLES DE DÉDOUBLEMENT (FOUJ) — split_rules.csv
# ══════════════════════════════════════════════════════════════════

SPLIT_RULES_CSV = """\
Rule_ID,Level,Primary_Subject,Primary_Type,Secondary_Subject,Secondary_Type,Coupling_Mode
R_FOUJ_01,1AM;2AM;3AM,ARABIC,TD,MATH,TD,SYNCHRONOUS_1H
R_FOUJ_02,4AM,ARABIC,TD,MATH,TD,SYNCHRONOUS_2H_SWAP
R_FOUJ_03,ALL,FRENCH,TD,ENGLISH,TD,SYNCHRONOUS_1H
R_FOUJ_04,ALL,PHYS,TP,SCIENCE,TP,SYNCHRONOUS_2H_SWAP
"""

# Durée du bloc et nombre de séances doubles selon le mode de couplage.
MODES_COUPLAGE = {
    "SYNCHRONOUS_1H":        {"heures": 1, "doubles": 0, "max_jour": 1},
    "SYNCHRONOUS_2H_SWAP":   {"heures": 2, "doubles": 1, "max_jour": 2},
}

REGLES_FOUJ = list(csv.DictReader(io.StringIO(SPLIT_RULES_CSV)))


def _regles_du_niveau(niveau: str):
    for regle in REGLES_FOUJ:
        portee = regle["Level"]
        if portee == "ALL" or niveau in portee.split(";"):
            yield regle


# ══════════════════════════════════════════════════════════════════
#  CORPS ENSEIGNANT — staff.csv
# ══════════════════════════════════════════════════════════════════

STAFF_CSV = """\
Teacher_ID,Qualified_Subjects,Max_Weekly_Hours,Requires_Reception,Unavailable_Windows
Ar_T1,ARABIC,20,True,
Ar_T2,ARABIC,20,True,
Ar_T3,ARABIC,20,True,
Ar_T4,ARABIC,20,True,
Ar_T5,ARABIC,20,True,
Ar_T6,ARABIC,20,True,
Ar_T7,ARABIC,20,True,
Ma_T1,MATH,20,True,
Ma_T2,MATH,20,True,
Ma_T3,MATH,20,True,
Ma_T4,MATH,20,True,
Ma_T5,MATH,20,True,
Ma_T6,MATH,20,True,
Ph_T1,PHYS,20,True,
Ph_T2,PHYS,20,True,
Ph_T3,PHYS,20,True,
Is_T1,ISLAMIC,20,True,
Is_T2,ISLAMIC,20,True,
Fr_T1,FRENCH,20,True,
Fr_T2,FRENCH,20,True,
Fr_T3,FRENCH,20,True,
Fr_T4,FRENCH,20,True,
Fr_T5,FRENCH,20,True,
Fr_T6,FRENCH,20,True,
En_T1,ENGLISH,20,True,
En_T2,ENGLISH,20,True,
En_T3,ENGLISH,20,True,
En_T4,ENGLISH,20,True,
Sc_T1,SCIENCE,20,True,
Sc_T2,SCIENCE,20,True,
Sc_T3,SCIENCE,20,True,
PE_T1,PE,20,True,
PE_T2,PE,20,True,
Art_T1,ART_MUSIC,20,True,
Info_T1,INFO,20,True,
Info_T2,INFO,20,True,
Soc_T1,HIST;GEO;CIVICS,20,True,
Soc_T2,HIST;GEO;CIVICS,20,True,
Soc_T3,HIST;GEO;CIVICS,20,True,
"""

# Le programme exige des matières que l'effectif fourni ne couvre pas.
# Mettre à True recrute le minimum d'enseignants manquants, signalés
# dans « enseignants_ajoutes », pour pouvoir tout de même produire un
# emploi du temps complet.
COMPLETER_EFFECTIF_MANQUANT = os.environ.get("CEM_COMPLETER_EFFECTIF") == "1"

professeurs: List[Professeur] = []
CORPS: Dict[str, List[int]] = {}
ID_PROF: Dict[str, int] = {}


def _creneaux_bloques(fenetres: str) -> set:
    """« 1:0;1;2 » → créneaux du jour 1, séances 0, 1 et 2."""
    bloques = set()
    for fenetre in filter(None, (f.strip() for f in fenetres.split("|"))):
        jour, _, seances = fenetre.partition(":")
        cibles = {int(x) for x in seances.split(";") if x.strip()}
        for creneau in creneaux:
            if creneau.index_jour == int(jour) and creneau.index_seance in cibles:
                bloques.add(creneau.id)
    return bloques


def _enregistrer(identifiant: str, codes, max_hebdo: int,
                 permanences: bool, indisponibilites: str = "") -> int:
    prof_id = len(professeurs) + 1
    nom, _, numero = identifiant.partition("_")
    bloques = _creneaux_bloques(indisponibilites)
    professeurs.append(Professeur(
        id=prof_id,
        nom=identifiant,
        prenom=nom,
        matieres_ids=[ID_MATIERE[c] for c in codes],
        creneaux_disponibles=({c.id for c in creneaux} - bloques) if bloques else set(),
        max_heures_consecutives=4,
        max_heures_par_jour=6,
        max_heures_par_semaine=max_hebdo,
        assure_permanences=permanences,
    ))
    ID_PROF[identifiant] = prof_id
    for code in codes:
        CORPS.setdefault(code, []).append(prof_id)
    return prof_id


for ligne in csv.DictReader(io.StringIO(STAFF_CSV)):
    _enregistrer(
        ligne["Teacher_ID"],
        [c.strip() for c in ligne["Qualified_Subjects"].split(";") if c.strip()],
        int(ligne["Max_Weekly_Hours"]),
        ligne["Requires_Reception"].strip().lower() == "true",
        ligne.get("Unavailable_Windows") or "",
    )

# ══════════════════════════════════════════════════════════════════
#  SERVICES À RÉPARTIR
#  Chaque ligne du programme devient un service à confier à un
#  enseignant qualifié, sans dépasser son plafond hebdomadaire.
# ══════════════════════════════════════════════════════════════════

# (code matière, heures, blocs de 2 h, max h/jour, type de salle,
#  identifiant de couplage, groupe)
services: List[tuple] = []

for classe in classes:
    programme = PROGRAMME[classe.niveau]
    couples = set()

    for regle in _regles_du_niveau(classe.niveau):
        mode = MODES_COUPLAGE[regle["Coupling_Mode"]]
        couplage = f"{classe.nom}:{regle['Rule_ID']}"
        for rang, code in enumerate((regle["Primary_Subject"],
                                     regle["Secondary_Subject"])):
            services.append((classe, code, mode["heures"], mode["doubles"],
                             mode["max_jour"],
                             programme[code]["Required_Room_Type"],
                             couplage, f"G{rang + 1}"))
            couples.add(code)

    for code, ligne in programme.items():
        heures = int(ligne["Hrs_Cours"])
        if heures:
            bloc = ligne["Cours_Block_Policy"]
            doubles = 1 if bloc == "ONE_2H_BLOCK_REST_1H" else 0
            services.append((classe, code, heures, doubles, 2 if doubles else 1,
                             ligne["Required_Room_Type"], None, ""))

        pratique = int(ligne["Hrs_Practice"])
        if pratique:
            taille = int(ligne["Practice_Block_Size"]) or pratique
            services.append((classe, code, pratique, pratique // taille, taille,
                             ligne["Required_Room_Type"], None, ""))

        if code not in couples:
            for colonne in ("Hrs_TD", "Hrs_TP"):
                heures = int(ligne[colonne])
                if heures:
                    services.append((classe, code, heures, 0, 1,
                                     ligne["Required_Room_Type"], None, ""))

# ── Répartition des services ──────────────────────────────────────
# Plusieurs matières sont à saturation : leur volume égale exactement le
# service cumulé des enseignants qualifiés. Une répartition à la ronde
# déborderait ; on confie donc chaque service à l'enseignant qui a le
# plus de marge, en gardant si possible le même pour le cours et le TD
# d'une classe.

def _repartir():
    """Retourne (cours affectés, services non affectés)."""
    reste = {p.id: (p.max_heures_par_semaine or 10 ** 6) for p in professeurs}
    titulaire: Dict[tuple, int] = {}
    affectes: List[CoursRequis] = []
    orphelins: List[tuple] = []
    identifiant = 1

    for service in sorted(services, key=lambda x: (-x[2], x[1], x[0].id)):
        classe, code, heures, doubles, max_jour, salle, couplage, groupe = service
        qualifies = CORPS.get(code, [])
        habituel = titulaire.get((classe.id, code))
        candidats = ([habituel] if habituel in qualifies
                     and reste[habituel] >= heures else [])
        candidats += sorted((p for p in qualifies
                             if p != habituel and reste[p] >= heures),
                            key=lambda p: -reste[p])
        if not candidats:
            orphelins.append(service)
            continue

        prof_id = candidats[0]
        reste[prof_id] -= heures
        titulaire.setdefault((classe.id, code), prof_id)
        affectes.append(CoursRequis(
            id=identifiant, classe_id=classe.id, matiere_id=ID_MATIERE[code],
            professeur_id=prof_id, heures_par_semaine=heures,
            type_salle_requis=salle, nb_seances_doubles=doubles,
            max_heures_par_jour=max_jour, couplage_id=couplage, groupe=groupe,
        ))
        identifiant += 1

    return affectes, orphelins


_besoin = defaultdict(int)
for _classe, _code, _heures, *_ in services:
    _besoin[_code] += _heures

matieres_non_couvertes = sorted(
    code for code in _besoin if not CORPS.get(code)
)

cours_requis, _orphelins = _repartir()

# Un service dure 1, 2 ou 3 heures et ne se coupe pas : diviser le volume
# par le plafond hebdomadaire sous-estime l'effectif nécessaire. On
# recrute donc un enseignant à la fois, jusqu'à ce que tout soit couvert.
enseignants_ajoutes: List[str] = []
if COMPLETER_EFFECTIF_MANQUANT:
    while _orphelins and len(enseignants_ajoutes) < 50:
        manquantes = sorted({service[1] for service in _orphelins})
        for code in manquantes:
            numero = sum(1 for x in enseignants_ajoutes
                         if x.startswith(code[:3].capitalize())) + 1
            identifiant = f"{code[:3].capitalize()}_X{numero}"
            _enregistrer(identifiant, [code], 20, True)
            enseignants_ajoutes.append(identifiant)
        cours_requis, _orphelins = _repartir()

services_non_affectes = [
    f"{classe.nom} / {code} ({heures} h)"
    for classe, code, heures, *_ in _orphelins
]

# ══════════════════════════════════════════════════════════════════
#  PARAMÉTRAGE
# ══════════════════════════════════════════════════════════════════

options = Options(
    limite_secondes=180,
    type_salle_ordinaire=TYPE_SALLE_ORDINAIRE,
    presence_minimale={"matin": 3},      # min_required_presence
    mode_heure_isolee="PER_SHIFT",
    permanences_max_par_prof=2,
)

ponderations = Ponderations(
    trous_professeurs=6,
    trous_doubles_professeurs=25,
    heure_isolee_professeur=12,
    jours_presence_professeurs=3,
    recompense_permanence=4,
    # Coût d'occupation par séance (index 0 = « slot 1 »).
    # Démarrage à 08:00 pénalisé davantage que la 4ᵉ séance, et dernière
    # séance de la journée pénalisée bien au-delà du reste.
    penalites_seance={0: 20, 3: 8, 4: 10, 5: 30, 6: 150},
    equite_derniere_seance=25,
    seance_soumise_a_equite=6,
    equilibrage_charge_classes=4,
)
