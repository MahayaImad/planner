"""
Classeur Excel : gabarit, export et import de toutes les données.

Saisir un établissement écran par écran demande des centaines de clics.
Un directeur préfère remplir un tableur qu'il connaît déjà, hors ligne,
et le téléverser d'un coup. Le gabarit produit ici est donc aussi le
format d'export : ce qui sort se re-téléverse tel quel, ce qui permet
de corriger en masse une donnée déjà saisie.

L'import est tout ou rien, comme celui du programme en CSV : un
établissement à moitié chargé serait pire qu'un import refusé, car le
responsable croirait sa saisie faite.

Les entités de référence sont appariées PAR NOM, pas par identifiant.
Un enseignant déjà en base est mis à jour, pas recréé — sans quoi les
emplois du temps existants perdraient leurs références. Une ligne
présente en base mais absente du fichier n'est jamais supprimée : la
suppression est une décision qui se prend écran par écran, avec ses
conséquences en cascade sous les yeux.
"""

import io
import unicodedata
from typing import Dict, List, Optional, Tuple

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from sqlalchemy.orm import Session

from ..models.class_ import Classe
from ..models.programme import LigneProgramme
from ..models.room import Salle
from ..models.subject import Matiere
from ..models.teacher import Professeur
from . import programme as service_programme

# Un classeur d'établissement ne dépasse pas quelques milliers de
# lignes ; au-delà, c'est un fichier qui n'a pas sa place ici.
TAILLE_MAX = 5 * 1024 * 1024
LIGNES_MAX = 5000

TYPES_SALLE = ["classique", "labo", "labo_bio", "labo_physique", "info",
               "sport", "atelier"]
NIVEAUX = ["primaire", "moyen", "secondaire"]

# (titre, clé, obligatoire, aide affichée dans le Lisez-moi)
FEUILLES: List[Dict] = [
    {
        "nom": "Matieres",
        "titre": "Matières",
        "aide": "Les disciplines enseignées. Le type de salle est celui "
                "qu'exige la matière : laissez vide pour une salle ordinaire.",
        "colonnes": [
            ("Nom", "nom", True, "Nom de la matière, tel qu'il apparaîtra partout."),
            ("Coefficient", "coefficient", False, "Poids de la matière. 1 par défaut."),
            ("Type de salle", "type_salle_requis", False,
             "labo, info, sport… Vide = salle ordinaire."),
        ],
    },
    {
        "nom": "Salles",
        "titre": "Salles",
        "aide": "Le parc de salles. Le type doit correspondre à celui exigé "
                "par les matières.",
        "colonnes": [
            ("Nom", "nom", True, "Identifiant de la salle : S1, Labo 2, Stade…"),
            ("Capacité", "capacite", False, "Nombre de places. 30 par défaut."),
            ("Type", "type", False, "classique par défaut."),
        ],
    },
    {
        "nom": "Enseignants",
        "titre": "Enseignants",
        "aide": "Le corps enseignant. Les matières se séparent par un "
                "point-virgule et doivent exister dans la feuille Matières.",
        "colonnes": [
            ("Nom", "nom", True, "Nom de famille."),
            ("Prénom", "prenom", True, "Prénom."),
            ("Email", "email", False, ""),
            ("Téléphone", "telephone", False, ""),
            ("Matières", "matieres", False,
             "Séparées par « ; ». Exemple : Mathématiques;Physique"),
            ("Heures consécutives max", "max_heures_consecutives", False,
             "Nombre d'heures d'affilée. 4 par défaut."),
            ("Heures par jour max", "max_heures_par_jour", False, "6 par défaut."),
            ("Heures par semaine max", "max_heures_par_semaine", False,
             "Service hebdomadaire. Vide = pas de plafond."),
            ("Assure les permanences", "assure_permanences", False,
             "oui ou non. oui par défaut."),
        ],
    },
    {
        "nom": "Classes",
        "titre": "Divisions",
        "aide": "Les divisions. La salle attitrée est celle où la division "
                "passe ses heures ordinaires ; elle doit exister dans la "
                "feuille Salles.",
        "colonnes": [
            ("Nom", "nom", True, "Nom de la division : 1AM1, 4AM A…"),
            ("Niveau", "niveau", True, "primaire, moyen ou secondaire."),
            ("Effectif", "effectif", False, "Nombre d'élèves. 30 par défaut."),
            ("Salle attitrée", "salle_attitree", False,
             "Nom d'une salle. Vide = aucune salle attitrée."),
            ("Heures par jour max", "max_heures_par_jour", False, "6 par défaut."),
        ],
    },
    {
        "nom": "Programme",
        "titre": "Programme annuel",
        "aide": "Qui enseigne quoi, à qui, combien d'heures. Pour un fouj "
                "(dédoublement), deux lignes partagent le même identifiant "
                "de couplage, l'une en G1 et l'autre en G2.",
        "colonnes": [
            ("Classe", "classe", True, "Nom d'une division."),
            ("Matière", "matiere", True, "Nom d'une matière."),
            ("Enseignant", "professeur", True,
             "Nom, ou « Prénom Nom » si plusieurs homonymes."),
            ("Heures par semaine", "heures", True, "Volume hebdomadaire."),
            ("Blocs de 2 h", "blocs_2h", False,
             "Nombre de séances doubles à réserver dans ce volume."),
            ("Max par jour", "max_par_jour", False,
             "Plafond de cette matière dans une journée."),
            ("Fouj (couplage)", "fouj", False,
             "Même libellé sur les deux lignes d'un dédoublement."),
            ("Groupe", "groupe", False, "G1 ou G2, pour un fouj."),
        ],
    },
]

_ENTETE = PatternFill("solid", fgColor="1E3A5F")
_TITRE = Font(bold=True, color="FFFFFF", size=11)


def _normaliser(texte) -> str:
    brut = "" if texte is None else str(texte)
    sans_accent = "".join(
        c for c in unicodedata.normalize("NFD", brut)
        if unicodedata.category(c) != "Mn")
    return "".join(c for c in sans_accent.lower() if c.isalnum())


def _texte(valeur) -> str:
    if valeur is None:
        return ""
    if isinstance(valeur, float) and valeur.is_integer():
        return str(int(valeur))
    return str(valeur).strip()


# ══════════════════════════════════════════════════════════════════
#  Gabarit et export
# ══════════════════════════════════════════════════════════════════

def _feuille_lisez_moi(classeur: Workbook) -> None:
    feuille = classeur.create_sheet("Lisez-moi", 0)
    feuille.column_dimensions["A"].width = 28
    feuille.column_dimensions["B"].width = 80

    lignes = [
        ("Classeur de données", ""),
        ("", ""),
        ("Mode d'emploi", "Remplissez les feuilles dans l'ordre des onglets : "
                          "une division renvoie à une salle, le programme "
                          "renvoie aux trois autres feuilles."),
        ("", "Ne renommez pas les onglets ni la ligne d'en-tête : l'import "
             "les reconnaît par leur nom."),
        ("", "L'import est tout ou rien. S'il reste une erreur, rien n'est "
             "écrit et la liste des erreurs vous est rendue, ligne par ligne."),
        ("", "Les lignes existantes sont appariées par leur nom et mises à "
             "jour. Rien n'est supprimé : une suppression se fait depuis "
             "l'écran correspondant, pour en voir les conséquences."),
        ("", ""),
    ]
    for titre, texte in lignes:
        feuille.append([titre, texte])
    feuille["A1"].font = Font(bold=True, size=14)

    for bloc in FEUILLES:
        feuille.append([])
        feuille.append([bloc["titre"], bloc["aide"]])
        feuille.cell(row=feuille.max_row, column=1).font = Font(bold=True, size=12)
        for titre, _cle, obligatoire, aide in bloc["colonnes"]:
            marque = "obligatoire" if obligatoire else "facultatif"
            feuille.append([f"   {titre}", f"({marque}) {aide}"])

    for ligne in feuille.iter_rows():
        for cellule in ligne:
            cellule.alignment = Alignment(vertical="top", wrap_text=True)


def _ecrire_feuille(classeur: Workbook, bloc: Dict, donnees: List[List]) -> None:
    feuille = classeur.create_sheet(bloc["nom"])
    titres = [c[0] for c in bloc["colonnes"]]
    feuille.append(titres)
    for position, titre in enumerate(titres, start=1):
        cellule = feuille.cell(row=1, column=position)
        cellule.fill = _ENTETE
        cellule.font = _TITRE
        cellule.alignment = Alignment(horizontal="center", vertical="center")
        feuille.column_dimensions[get_column_letter(position)].width = \
            max(14, min(30, len(titre) + 6))
    for ligne in donnees:
        feuille.append(ligne)
    feuille.freeze_panes = "A2"


def _listes_deroulantes(classeur: Workbook) -> None:
    """Des choix guidés valent mieux qu'un contrôle après coup."""
    contraintes = [
        ("Salles", 3, TYPES_SALLE),
        ("Classes", 2, NIVEAUX),
        ("Programme", 8, ["G1", "G2"]),
        ("Enseignants", 9, ["oui", "non"]),
    ]
    for nom, colonne, valeurs in contraintes:
        if nom not in classeur.sheetnames:
            continue
        feuille = classeur[nom]
        validation = DataValidation(
            type="list", formula1='"' + ",".join(valeurs) + '"',
            allow_blank=True, showDropDown=False)
        feuille.add_data_validation(validation)
        lettre = get_column_letter(colonne)
        validation.add(f"{lettre}2:{lettre}1000")


def construire(db: Session, ecole_id: int, avec_donnees: bool) -> bytes:
    """Gabarit vide, ou export complet si avec_donnees."""
    classeur = Workbook()
    classeur.remove(classeur.active)

    contenu: Dict[str, List[List]] = {bloc["nom"]: [] for bloc in FEUILLES}
    if avec_donnees:
        contenu["Matieres"] = [
            [m.nom, m.coefficient, m.type_salle_requis or ""]
            for m in db.query(Matiere).filter(
                Matiere.ecole_id == ecole_id).order_by(Matiere.nom)
        ]
        contenu["Salles"] = [
            [s.nom, s.capacite, s.type]
            for s in db.query(Salle).filter(
                Salle.ecole_id == ecole_id).order_by(Salle.nom)
        ]
        contenu["Enseignants"] = [
            [p.nom, p.prenom, p.email or "", p.telephone or "",
             ";".join(m.nom for m in p.matieres),
             p.max_heures_consecutives, p.max_heures_par_jour,
             p.max_heures_par_semaine or "",
             "oui" if p.assure_permanences else "non"]
            for p in db.query(Professeur).filter(
                Professeur.ecole_id == ecole_id).order_by(Professeur.nom)
        ]
        contenu["Classes"] = [
            [c.nom, c.niveau, c.effectif,
             c.salle_attitree.nom if c.salle_attitree else "",
             c.max_heures_par_jour]
            for c in db.query(Classe).filter(
                Classe.ecole_id == ecole_id).order_by(Classe.nom)
        ]
        contenu["Programme"] = [
            [l.classe.nom if l.classe else "",
             l.matiere.nom if l.matiere else "",
             l.professeur.nom_complet if l.professeur else "",
             l.heures_par_semaine, l.nb_seances_doubles, l.max_heures_par_jour,
             (l.couplage_id or "").split(":", 1)[-1] if l.couplage_id else "",
             l.groupe or ""]
            for l in service_programme.lignes(db, ecole_id)
        ]

    _feuille_lisez_moi(classeur)
    for bloc in FEUILLES:
        _ecrire_feuille(classeur, bloc, contenu[bloc["nom"]])
    _listes_deroulantes(classeur)

    tampon = io.BytesIO()
    classeur.save(tampon)
    return tampon.getvalue()


# ══════════════════════════════════════════════════════════════════
#  Import
# ══════════════════════════════════════════════════════════════════

class _Rapport:
    """Ce que l'import a compris du fichier, avant toute écriture."""

    def __init__(self):
        self.erreurs: List[str] = []
        self.crees: Dict[str, int] = {}
        self.modifies: Dict[str, int] = {}
        self.absents_du_fichier: Dict[str, List[str]] = {}

    def en_dict(self, applique: bool) -> Dict:
        return {
            "valide": not self.erreurs,
            "applique": applique,
            "erreurs": self.erreurs,
            "crees": self.crees,
            "modifies": self.modifies,
            "presents_en_base_absents_du_fichier": self.absents_du_fichier,
        }


def _lire_feuille(classeur, bloc: Dict, rapport: _Rapport) -> List[Dict]:
    """Lignes d'une feuille, indexées par clé de colonne."""
    if bloc["nom"] not in classeur.sheetnames:
        rapport.erreurs.append(
            f"Onglet « {bloc['nom']} » absent du classeur.")
        return []
    feuille = classeur[bloc["nom"]]
    lignes = list(feuille.iter_rows(values_only=True))
    if not lignes:
        return []

    # L'en-tête est reconnu par le nom des colonnes, pas par leur ordre :
    # un tableur réordonné reste lisible.
    entete = [_normaliser(c) for c in lignes[0]]
    positions: Dict[str, int] = {}
    for titre, cle, _obligatoire, _aide in bloc["colonnes"]:
        cherche = _normaliser(titre)
        if cherche in entete:
            positions[cle] = entete.index(cherche)

    manquantes = [titre for titre, cle, obligatoire, _ in bloc["colonnes"]
                  if obligatoire and cle not in positions]
    if manquantes:
        rapport.erreurs.append(
            f"{bloc['nom']} : colonne(s) absente(s) — " + ", ".join(manquantes))
        return []

    lues = []
    for numero, ligne in enumerate(lignes[1:], start=2):
        if not any(_texte(c) for c in ligne):
            continue
        if len(lues) >= LIGNES_MAX:
            rapport.erreurs.append(
                f"{bloc['nom']} : plus de {LIGNES_MAX} lignes.")
            break
        valeurs = {cle: _texte(ligne[pos]) if pos < len(ligne) else ""
                   for cle, pos in positions.items()}
        valeurs["_ligne"] = numero
        lues.append(valeurs)
    return lues


def _entier(valeur: str, defaut: Optional[int], champ: str, ligne: int,
            feuille: str, rapport: _Rapport) -> Optional[int]:
    if not valeur:
        return defaut
    try:
        return int(float(valeur.replace(",", ".")))
    except ValueError:
        rapport.erreurs.append(
            f"{feuille} ligne {ligne} : « {valeur} » n'est pas un nombre "
            f"({champ}).")
        return None


def analyser(db: Session, ecole_id: int, contenu: bytes) -> Tuple[Dict, Dict]:
    """
    Lit et valide le classeur sans rien écrire.

    Retourne (rapport, données prêtes à appliquer).
    """
    rapport = _Rapport()
    if len(contenu) > TAILLE_MAX:
        rapport.erreurs.append(
            f"Fichier trop volumineux ({len(contenu) // 1024} Kio).")
        return rapport.en_dict(False), {}
    try:
        classeur = load_workbook(io.BytesIO(contenu), data_only=True,
                                 read_only=True)
    except Exception:                                   # noqa: BLE001
        rapport.erreurs.append(
            "Fichier illisible : attendu un classeur Excel (.xlsx).")
        return rapport.en_dict(False), {}

    par_feuille = {bloc["nom"]: _lire_feuille(classeur, bloc, rapport)
                   for bloc in FEUILLES}
    if rapport.erreurs:
        return rapport.en_dict(False), {}

    # ── Existant, apparié par nom ────────────────────────────────
    matieres = {_normaliser(m.nom): m for m in db.query(Matiere).filter(
        Matiere.ecole_id == ecole_id)}
    salles = {_normaliser(s.nom): s for s in db.query(Salle).filter(
        Salle.ecole_id == ecole_id)}
    classes = {_normaliser(c.nom): c for c in db.query(Classe).filter(
        Classe.ecole_id == ecole_id)}
    professeurs = {_normaliser(f"{p.nom}{p.prenom}"): p
                   for p in db.query(Professeur).filter(
                       Professeur.ecole_id == ecole_id)}

    prepare: Dict[str, List[Dict]] = {}

    # ── Matières ─────────────────────────────────────────────────
    vues = set()
    prepare["Matieres"] = []
    for ligne in par_feuille["Matieres"]:
        nom = ligne["nom"]
        if not nom:
            rapport.erreurs.append(f"Matieres ligne {ligne['_ligne']} : nom vide.")
            continue
        cle = _normaliser(nom)
        if cle in vues:
            rapport.erreurs.append(
                f"Matieres ligne {ligne['_ligne']} : « {nom} » apparaît deux fois.")
            continue
        vues.add(cle)
        coefficient = ligne.get("coefficient", "")
        try:
            coefficient = float(coefficient.replace(",", ".")) if coefficient else 1.0
        except ValueError:
            rapport.erreurs.append(
                f"Matieres ligne {ligne['_ligne']} : coefficient « {coefficient} » "
                f"illisible.")
            continue
        prepare["Matieres"].append({
            "cle": cle, "nom": nom, "coefficient": coefficient,
            "type_salle_requis": ligne.get("type_salle_requis") or None,
        })

    # ── Salles ───────────────────────────────────────────────────
    vues = set()
    prepare["Salles"] = []
    for ligne in par_feuille["Salles"]:
        nom = ligne["nom"]
        if not nom:
            rapport.erreurs.append(f"Salles ligne {ligne['_ligne']} : nom vide.")
            continue
        cle = _normaliser(nom)
        if cle in vues:
            rapport.erreurs.append(
                f"Salles ligne {ligne['_ligne']} : « {nom} » apparaît deux fois.")
            continue
        vues.add(cle)
        capacite = _entier(ligne.get("capacite", ""), 30, "capacité",
                           ligne["_ligne"], "Salles", rapport)
        if capacite is None:
            continue
        prepare["Salles"].append({
            "cle": cle, "nom": nom, "capacite": capacite,
            "type": ligne.get("type") or "classique",
        })

    # Noms de salles connus après import, pour les divisions.
    salles_connues = set(salles) | {s["cle"] for s in prepare["Salles"]}
    matieres_connues = set(matieres) | {m["cle"] for m in prepare["Matieres"]}

    # ── Enseignants ──────────────────────────────────────────────
    vues = set()
    prepare["Enseignants"] = []
    for ligne in par_feuille["Enseignants"]:
        nom, prenom = ligne["nom"], ligne["prenom"]
        numero = ligne["_ligne"]
        if not nom or not prenom:
            rapport.erreurs.append(
                f"Enseignants ligne {numero} : nom et prénom sont obligatoires.")
            continue
        cle = _normaliser(f"{nom}{prenom}")
        if cle in vues:
            rapport.erreurs.append(
                f"Enseignants ligne {numero} : « {prenom} {nom} » apparaît "
                f"deux fois.")
            continue
        vues.add(cle)

        libelles = [m.strip() for m in (ligne.get("matieres") or "").split(";")
                    if m.strip()]
        inconnues = [m for m in libelles if _normaliser(m) not in matieres_connues]
        if inconnues:
            rapport.erreurs.append(
                f"Enseignants ligne {numero} : matière(s) inconnue(s) — "
                + ", ".join(inconnues))
            continue

        consecutives = _entier(ligne.get("max_heures_consecutives", ""), 4,
                               "heures consécutives", numero, "Enseignants", rapport)
        par_jour = _entier(ligne.get("max_heures_par_jour", ""), 6,
                           "heures par jour", numero, "Enseignants", rapport)
        par_semaine = _entier(ligne.get("max_heures_par_semaine", ""), None,
                              "heures par semaine", numero, "Enseignants", rapport)
        if consecutives is None or par_jour is None:
            continue
        prepare["Enseignants"].append({
            "cle": cle, "nom": nom, "prenom": prenom,
            "email": ligne.get("email") or None,
            "telephone": ligne.get("telephone") or None,
            "matieres": [_normaliser(m) for m in libelles],
            "max_heures_consecutives": consecutives,
            "max_heures_par_jour": par_jour,
            "max_heures_par_semaine": par_semaine,
            "assure_permanences":
                _normaliser(ligne.get("assure_permanences", "")) not in
                {"non", "no", "faux", "false", "0"},
        })

    # ── Divisions ────────────────────────────────────────────────
    vues = set()
    prepare["Classes"] = []
    for ligne in par_feuille["Classes"]:
        nom, numero = ligne["nom"], ligne["_ligne"]
        if not nom:
            rapport.erreurs.append(f"Classes ligne {numero} : nom vide.")
            continue
        cle = _normaliser(nom)
        if cle in vues:
            rapport.erreurs.append(
                f"Classes ligne {numero} : « {nom} » apparaît deux fois.")
            continue
        vues.add(cle)
        niveau = ligne.get("niveau") or ""
        if not niveau:
            rapport.erreurs.append(f"Classes ligne {numero} : niveau vide.")
            continue
        salle = ligne.get("salle_attitree") or ""
        if salle and _normaliser(salle) not in salles_connues:
            rapport.erreurs.append(
                f"Classes ligne {numero} : salle « {salle} » inconnue.")
            continue
        effectif = _entier(ligne.get("effectif", ""), 30, "effectif", numero,
                           "Classes", rapport)
        par_jour = _entier(ligne.get("max_heures_par_jour", ""), 6,
                           "heures par jour", numero, "Classes", rapport)
        if effectif is None or par_jour is None:
            continue
        prepare["Classes"].append({
            "cle": cle, "nom": nom, "niveau": niveau, "effectif": effectif,
            "salle_attitree": _normaliser(salle) if salle else None,
            "max_heures_par_jour": par_jour,
        })

    prepare["Programme"] = par_feuille["Programme"]

    # Ce qui existe en base sans figurer au fichier : signalé, jamais
    # supprimé.
    rapport.absents_du_fichier = {
        "Matieres": sorted(m.nom for cle, m in matieres.items()
                           if cle not in {x["cle"] for x in prepare["Matieres"]}),
        "Salles": sorted(s.nom for cle, s in salles.items()
                         if cle not in {x["cle"] for x in prepare["Salles"]}),
        "Enseignants": sorted(
            p.nom_complet for cle, p in professeurs.items()
            if cle not in {x["cle"] for x in prepare["Enseignants"]}),
        "Classes": sorted(c.nom for cle, c in classes.items()
                          if cle not in {x["cle"] for x in prepare["Classes"]}),
    }
    return rapport.en_dict(False), prepare


def _csv_du_programme(lignes_lues: List[Dict]) -> str:
    """Le programme repasse par l'analyseur CSV déjà éprouvé."""
    import csv as _csv
    tampon = io.StringIO()
    redacteur = _csv.writer(tampon)
    redacteur.writerow(service_programme.ENTETE_EXPORT)
    for ligne in lignes_lues:
        redacteur.writerow([
            ligne.get("classe", ""), ligne.get("matiere", ""),
            ligne.get("professeur", ""), ligne.get("heures", ""),
            ligne.get("blocs_2h", ""), ligne.get("max_par_jour", ""),
            ligne.get("fouj", ""), ligne.get("groupe", ""),
        ])
    return tampon.getvalue()


def importer(db: Session, ecole_id: int, contenu: bytes,
             appliquer: bool = True) -> Dict:
    """
    Charge un classeur. Tout ou rien.

    Les données de référence sont écrites d'abord — sans validation, le
    programme ne pourrait pas désigner une matière créée par le même
    fichier — puis le programme est analysé dans la même transaction.
    La moindre erreur annule l'ensemble.
    """
    rapport_dict, prepare = analyser(db, ecole_id, contenu)
    if not rapport_dict["valide"]:
        return rapport_dict

    rapport = _Rapport()
    rapport.absents_du_fichier = rapport_dict["presents_en_base_absents_du_fichier"]
    try:
        matieres = {_normaliser(m.nom): m for m in db.query(Matiere).filter(
            Matiere.ecole_id == ecole_id)}
        salles = {_normaliser(s.nom): s for s in db.query(Salle).filter(
            Salle.ecole_id == ecole_id)}
        classes = {_normaliser(c.nom): c for c in db.query(Classe).filter(
            Classe.ecole_id == ecole_id)}
        professeurs = {_normaliser(f"{p.nom}{p.prenom}"): p
                       for p in db.query(Professeur).filter(
                           Professeur.ecole_id == ecole_id)}

        compte = {nom: [0, 0] for nom in
                  ("Matieres", "Salles", "Enseignants", "Classes")}

        for donnees in prepare["Matieres"]:
            existante = matieres.get(donnees["cle"])
            if existante is None:
                existante = Matiere(ecole_id=ecole_id, nom=donnees["nom"])
                db.add(existante)
                matieres[donnees["cle"]] = existante
                compte["Matieres"][0] += 1
            else:
                compte["Matieres"][1] += 1
            existante.nom = donnees["nom"]
            existante.coefficient = donnees["coefficient"]
            existante.type_salle_requis = donnees["type_salle_requis"]

        for donnees in prepare["Salles"]:
            existante = salles.get(donnees["cle"])
            if existante is None:
                existante = Salle(ecole_id=ecole_id, nom=donnees["nom"])
                db.add(existante)
                salles[donnees["cle"]] = existante
                compte["Salles"][0] += 1
            else:
                compte["Salles"][1] += 1
            existante.nom = donnees["nom"]
            existante.capacite = donnees["capacite"]
            existante.type = donnees["type"]

        for donnees in prepare["Enseignants"]:
            existant = professeurs.get(donnees["cle"])
            if existant is None:
                existant = Professeur(ecole_id=ecole_id, nom=donnees["nom"],
                                      prenom=donnees["prenom"])
                db.add(existant)
                professeurs[donnees["cle"]] = existant
                compte["Enseignants"][0] += 1
            else:
                compte["Enseignants"][1] += 1
            existant.nom = donnees["nom"]
            existant.prenom = donnees["prenom"]
            existant.email = donnees["email"]
            existant.telephone = donnees["telephone"]
            existant.max_heures_consecutives = donnees["max_heures_consecutives"]
            existant.max_heures_par_jour = donnees["max_heures_par_jour"]
            existant.max_heures_par_semaine = donnees["max_heures_par_semaine"]
            existant.assure_permanences = donnees["assure_permanences"]
            existant.matieres = [matieres[c] for c in donnees["matieres"]]

        for donnees in prepare["Classes"]:
            existante = classes.get(donnees["cle"])
            if existante is None:
                existante = Classe(ecole_id=ecole_id, nom=donnees["nom"],
                                   niveau=donnees["niveau"])
                db.add(existante)
                classes[donnees["cle"]] = existante
                compte["Classes"][0] += 1
            else:
                compte["Classes"][1] += 1
            existante.nom = donnees["nom"]
            existante.niveau = donnees["niveau"]
            existante.effectif = donnees["effectif"]
            existante.max_heures_par_jour = donnees["max_heures_par_jour"]
            existante.salle_attitree_id = (
                salles[donnees["salle_attitree"]].id
                if donnees["salle_attitree"] else None)

        # Les identifiants doivent exister avant que le programme ne les
        # désigne : l'analyse du programme relit la base.
        db.flush()
        for donnees in prepare["Classes"]:
            if donnees["salle_attitree"]:
                classes[donnees["cle"]].salle_attitree_id = \
                    salles[donnees["salle_attitree"]].id
        db.flush()

        rapport.crees = {nom: valeurs[0] for nom, valeurs in compte.items()}
        rapport.modifies = {nom: valeurs[1] for nom, valeurs in compte.items()}

        lignes_programme, erreurs = service_programme.analyser_csv(
            db, ecole_id, _csv_du_programme(prepare["Programme"]))
        if erreurs:
            db.rollback()
            rapport.erreurs = ["Programme : " + e for e in erreurs]
            return rapport.en_dict(False)

        db.query(LigneProgramme).filter(
            LigneProgramme.ecole_id == ecole_id).delete()
        for ligne in lignes_programme:
            db.add(LigneProgramme(ecole_id=ecole_id, **ligne))
        rapport.crees["Programme"] = len(lignes_programme)
        rapport.modifies["Programme"] = 0

        if appliquer:
            db.commit()
        else:
            db.rollback()
        return rapport.en_dict(appliquer)
    except Exception:                                   # noqa: BLE001
        db.rollback()
        raise
