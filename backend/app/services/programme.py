"""
Programme annuel : lecture, écriture, import et export CSV.

L'import est tout ou rien. Un programme à moitié chargé serait pire
qu'un import refusé : le responsable croirait sa saisie faite, et la
génération porterait sur un programme amputé sans le signaler. Toutes
les lignes sont donc validées avant la moindre écriture, et les erreurs
sont rendues avec leur numéro de ligne.
"""

import csv
import io
import unicodedata
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models.class_ import Classe
from ..models.programme import LigneProgramme
from ..models.subject import Matiere
from ..models.teacher import Professeur

# Colonnes acceptées à l'import. Plusieurs écritures sont tolérées : un
# fichier produit sous Excel ne respecte jamais exactement un gabarit.
COLONNES = {
    "classe": {"classe", "class", "classid", "division"},
    "matiere": {"matiere", "subject", "discipline", "module"},
    "professeur": {"professeur", "enseignant", "teacher", "prof"},
    "heures": {"heures", "heureshebdo", "heuresparsemaine", "hours", "volume"},
    "blocs": {"blocs2h", "blocs", "seancesdoubles", "nbseancesdoubles", "doubles"},
    "maxjour": {"maxparjour", "maxheuresparjour", "maxjour", "plafondjour"},
    "fouj": {"fouj", "couplage", "couplageid", "groupeid"},
    "groupe": {"groupe", "demigroupe", "group"},
}

ENTETE_EXPORT = ["classe", "matiere", "professeur", "heures", "blocs_2h",
                 "max_par_jour", "fouj", "groupe"]


def _normaliser(texte: str) -> str:
    """Minuscules, sans accent ni séparateur : « Matière » → « matiere »."""
    sans_accent = "".join(
        c for c in unicodedata.normalize("NFD", texte or "")
        if unicodedata.category(c) != "Mn")
    return "".join(c for c in sans_accent.lower() if c.isalnum())


def _index_colonnes(entete: List[str]) -> Dict[str, int]:
    trouvees: Dict[str, int] = {}
    for position, nom in enumerate(entete or []):
        cle_normalisee = _normaliser(nom)
        for cle, alias in COLONNES.items():
            if cle_normalisee in alias and cle not in trouvees:
                trouvees[cle] = position
    return trouvees


# ══════════════════════════════════════════════════════════════════
#  Lecture
# ══════════════════════════════════════════════════════════════════

def lignes(db: Session, ecole_id: int) -> List[LigneProgramme]:
    return db.query(LigneProgramme).filter(
        LigneProgramme.ecole_id == ecole_id,
    ).order_by(LigneProgramme.classe_id, LigneProgramme.id).all()


def cours_requis(db: Session, ecole_id: int) -> List[Dict]:
    """Programme au format attendu par le solveur."""
    return [{
        "classe_id": l.classe_id,
        "matiere_id": l.matiere_id,
        "professeur_id": l.professeur_id,
        "heures_par_semaine": l.heures_par_semaine,
        "nb_seances_doubles": l.nb_seances_doubles,
        "max_heures_par_jour": l.max_heures_par_jour,
        "couplage_id": l.couplage_id,
        "groupe": l.groupe or "",
    } for l in lignes(db, ecole_id)]


def exporter_csv(db: Session, ecole_id: int) -> str:
    """Programme au format d'import : l'aller-retour doit être fidèle."""
    tampon = io.StringIO()
    redacteur = csv.writer(tampon)
    redacteur.writerow(ENTETE_EXPORT)
    for l in lignes(db, ecole_id):
        redacteur.writerow([
            l.classe.nom if l.classe else "",
            l.matiere.nom if l.matiere else "",
            l.professeur.nom_complet if l.professeur else "",
            l.heures_par_semaine,
            l.nb_seances_doubles,
            l.max_heures_par_jour,
            l.couplage_id or "",
            l.groupe or "",
        ])
    return tampon.getvalue()


def modele_csv() -> str:
    """Gabarit commenté, à télécharger puis compléter."""
    return (
        ",".join(ENTETE_EXPORT) + "\n"
        "4AM A,Mathématiques,Fatima Meziane,5,1,2,,\n"
        "4AM A,Langue Arabe,Karim Benali,5,1,2,,\n"
        "4AM A,Sciences Physiques,Amina Hadj,2,0,1,TP-SCIENCES,G1\n"
        "4AM A,Sciences Naturelles,Yasmine Cherif,2,0,1,TP-SCIENCES,G2\n"
    )


# ══════════════════════════════════════════════════════════════════
#  Import
# ══════════════════════════════════════════════════════════════════

def _table_de_correspondance(db: Session, ecole_id: int):
    """Index par nom, pour retrouver les entités citées dans le fichier."""
    classes, matieres, professeurs = {}, {}, {}

    for c in db.query(Classe).filter(Classe.ecole_id == ecole_id):
        classes[_normaliser(c.nom)] = c
    for m in db.query(Matiere).filter(Matiere.ecole_id == ecole_id):
        matieres[_normaliser(m.nom)] = m

    for p in db.query(Professeur).filter(Professeur.ecole_id == ecole_id):
        # Un enseignant peut être cité « Prénom Nom », « Nom Prénom » ou
        # par son seul nom quand il n'y a pas d'homonyme.
        for ecriture in (f"{p.prenom} {p.nom}", f"{p.nom} {p.prenom}", p.nom):
            cle = _normaliser(ecriture)
            if cle in professeurs and professeurs[cle] is not p:
                professeurs[cle] = None          # homonyme : lever l'ambiguïté
            else:
                professeurs.setdefault(cle, p)
    return classes, matieres, professeurs


def analyser_csv(db: Session, ecole_id: int, contenu: str
                 ) -> Tuple[List[Dict], List[str]]:
    """
    Analyse un fichier et retourne (lignes valides, erreurs).

    Rien n'est écrit ici : l'appelant décide, au vu des erreurs, d'écrire
    ou d'abandonner.
    """
    erreurs: List[str] = []
    if not contenu.strip():
        return [], ["Le fichier est vide."]

    # Excel francophone exporte volontiers en point-virgule.
    try:
        dialecte = csv.Sniffer().sniff(contenu[:2000], delimiters=",;\t")
    except csv.Error:
        dialecte = csv.excel
    lecteur = csv.reader(io.StringIO(contenu), dialecte)

    try:
        entete = next(lecteur)
    except StopIteration:
        return [], ["Le fichier ne contient aucune ligne."]

    colonnes = _index_colonnes(entete)
    obligatoires = ["classe", "matiere", "professeur", "heures"]
    absentes = [c for c in obligatoires if c not in colonnes]
    if absentes:
        return [], [
            "Colonnes absentes : " + ", ".join(absentes) + ". "
            "L'en-tête attendu est : " + ", ".join(ENTETE_EXPORT) + "."
        ]

    classes, matieres, professeurs = _table_de_correspondance(db, ecole_id)
    if not classes or not matieres or not professeurs:
        return [], ["Créez d'abord les classes, matières et enseignants : "
                    "le programme les désigne par leur nom."]

    valides: List[Dict] = []
    for numero, ligne in enumerate(lecteur, start=2):
        if not any(cellule.strip() for cellule in ligne):
            continue

        def champ(cle: str, defaut: str = "") -> str:
            position = colonnes.get(cle)
            if position is None or position >= len(ligne):
                return defaut
            return ligne[position].strip()

        problemes = []
        classe = classes.get(_normaliser(champ("classe")))
        if classe is None:
            problemes.append(f"classe « {champ('classe')} » inconnue")
        matiere = matieres.get(_normaliser(champ("matiere")))
        if matiere is None:
            problemes.append(f"matière « {champ('matiere')} » inconnue")

        cle_prof = _normaliser(champ("professeur"))
        professeur = professeurs.get(cle_prof, "absent")
        if professeur == "absent":
            problemes.append(f"enseignant « {champ('professeur')} » inconnu")
        elif professeur is None:
            problemes.append(
                f"plusieurs enseignants répondent à « {champ('professeur')} » : "
                f"précisez le prénom")

        def entier(cle: str, defaut: int) -> Optional[int]:
            brut = champ(cle)
            if not brut:
                return defaut
            try:
                return int(float(brut.replace(",", ".")))
            except ValueError:
                problemes.append(f"« {brut} » n'est pas un nombre ({cle})")
                return None

        heures = entier("heures", 0)
        blocs = entier("blocs", 0)
        max_jour = entier("maxjour", 0)

        if heures is not None and heures <= 0 and not problemes:
            problemes.append("le volume horaire doit être positif")
        if (heures and blocs is not None and blocs * 2 > heures):
            problemes.append(
                f"{blocs} bloc(s) de 2 h demandé(s) pour un volume de {heures} h")

        if problemes:
            erreurs.append(f"ligne {numero} : " + " ; ".join(problemes))
            continue

        if matiere is not None and professeur is not None and professeur != "absent":
            if professeur.matieres and matiere not in professeur.matieres:
                erreurs.append(
                    f"ligne {numero} : {professeur.nom_complet} n'enseigne pas "
                    f"« {matiere.nom} »")
                continue

        groupe = champ("groupe").upper()
        couplage = champ("fouj") or None
        if couplage and not groupe:
            groupe = "G1"
        if groupe and not couplage:
            erreurs.append(
                f"ligne {numero} : un demi-groupe est indiqué sans identifiant "
                f"de fouj — les deux vont de pair")
            continue

        valides.append({
            "classe_id": classe.id,
            "matiere_id": matiere.id,
            "professeur_id": professeur.id,
            "heures_par_semaine": heures,
            "nb_seances_doubles": blocs or 0,
            "max_heures_par_jour": max_jour or (2 if blocs else 1),
            # L'identifiant de fouj est propre à une classe : deux
            # divisions peuvent réutiliser le même libellé sans se
            # mélanger.
            "couplage_id": f"{classe.id}:{couplage}" if couplage else None,
            "groupe": groupe,
        })

    # Un fouj s'apparie forcément par deux.
    couples: Dict[str, List[str]] = {}
    for ligne in valides:
        if ligne["couplage_id"]:
            couples.setdefault(ligne["couplage_id"], []).append(ligne["groupe"])
    for identifiant, groupes in couples.items():
        libelle = identifiant.split(":", 1)[1]
        if len(groupes) != 2:
            erreurs.append(
                f"fouj « {libelle} » : {len(groupes)} ligne(s) au lieu de 2. "
                f"Un dédoublement associe exactement deux demi-groupes.")
        elif len(set(groupes)) != 2:
            erreurs.append(
                f"fouj « {libelle} » : les deux lignes portent le même "
                f"demi-groupe ({groupes[0]}).")

    return valides, erreurs


def remplacer(db: Session, ecole_id: int, nouvelles: List[Dict]) -> int:
    """Remplace tout le programme. Retourne le nombre de lignes écrites."""
    db.query(LigneProgramme).filter(
        LigneProgramme.ecole_id == ecole_id).delete()
    for ligne in nouvelles:
        db.add(LigneProgramme(ecole_id=ecole_id, **ligne))
    db.commit()
    return len(nouvelles)
