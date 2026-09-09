"""
Tests de l'API : authentification, sécurité et génération asynchrone.

    python3 tests/test_api.py
"""

import os
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{RACINE}/test_api.db")

BASE = Path(os.environ["DATABASE_URL"].replace("sqlite:///", ""))
if BASE.exists():
    BASE.unlink()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import auth as service_auth  # noqa: E402

client = TestClient(app)


# ══════════════════════════════════════════════════════════════════
#  Mots de passe et jetons
# ══════════════════════════════════════════════════════════════════

def test_mot_de_passe_hache_avec_scrypt():
    empreinte = service_auth.hacher_mot_de_passe("motdepasse-solide")
    assert empreinte.startswith("scrypt$")
    # Deux hachages du même mot de passe diffèrent : le sel est aléatoire.
    assert empreinte != service_auth.hacher_mot_de_passe("motdepasse-solide")
    assert service_auth.verifier_mot_de_passe("motdepasse-solide", empreinte)
    assert not service_auth.verifier_mot_de_passe("autre", empreinte)
    assert not service_auth.doit_etre_rehache(empreinte)


def test_empreinte_heritee_est_relue_puis_remplacee():
    """Les comptes créés avant la migration doivent rester utilisables."""
    try:
        from passlib.hash import sha256_crypt
    except ImportError:
        return
    ancienne = sha256_crypt.hash("ancien-secret")
    assert service_auth.verifier_mot_de_passe("ancien-secret", ancienne)
    assert service_auth.doit_etre_rehache(ancienne)


def test_jeton_altere_est_rejete():
    jeton = service_auth.creer_token(1, 2, "a@b.dz")
    assert service_auth.decoder_token(jeton) is not None
    assert service_auth.decoder_token(jeton[:-4] + "AAAA") is None
    assert service_auth.decoder_token("nimportequoi") is None


def test_algorithme_none_est_rejete():
    """Un jeton annonçant « alg: none » ne doit jamais passer."""
    import base64
    import json
    jeton = service_auth.creer_token(1, 2, "a@b.dz")
    entete = base64.urlsafe_b64encode(
        json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    forge = f"{entete}.{jeton.split('.')[1]}."
    assert service_auth.decoder_token(forge) is None


def test_cle_secrete_obligatoire_hors_developpement():
    from app.config import CLE_PAR_DEFAUT, Settings
    reglages = Settings(SECRET_KEY=CLE_PAR_DEFAUT, DEBUG=False)
    try:
        reglages.valider()
        assert False, "une clé par défaut ne doit pas être acceptée"
    except RuntimeError as e:
        assert "SECRET_KEY" in str(e)


def test_joker_cors_refuse_hors_developpement():
    from app.config import Settings
    reglages = Settings(SECRET_KEY="x" * 40, CORS_ORIGINS="*", DEBUG=False)
    try:
        reglages.valider()
        assert False, "le joker CORS ne doit pas être accepté"
    except RuntimeError as e:
        assert "CORS" in str(e)


# ══════════════════════════════════════════════════════════════════
#  Parcours complet
# ══════════════════════════════════════════════════════════════════

# (nom, type de salle exigé, heures/semaine, blocs de 2 h)
PROGRAMME = [("Maths", None, 4, 1), ("Arabe", None, 4, 1),
             ("Français", None, 3, 0), ("Sport", "sport", 2, 1)]


def _etablissement(suffixe: str, nb_classes: int = 2):
    """Inscrit une école avec ses ressources ; renvoie (entêtes, ids)."""
    r = client.post("/auth/inscrire", json={
        "ecole": {"nom": f"CEM {suffixe}", "email": f"{suffixe}@test.dz"},
        "admin": {"nom": "A", "prenom": "B", "email": f"admin{suffixe}@test.dz",
                  "mot_de_passe": "motdepasse-solide"}})
    assert r.status_code == 201, r.text
    entetes = {"Authorization": f"Bearer {r.json()['access_token']}"}

    matieres = {nom: client.post(
        "/matieres/", json={"nom": nom, "type_salle_requis": salle},
        headers=entetes).json()["id"] for nom, salle, _, _ in PROGRAMME}

    for i in range(nb_classes + 1):
        client.post("/salles/", json={"nom": f"S{i + 1}", "capacite": 40,
                                      "type": "classique"}, headers=entetes)
    for i in range(max(1, nb_classes // 4)):
        client.post("/salles/", json={"nom": f"Stade {i + 1}", "capacite": 60,
                                      "type": "sport"}, headers=entetes)

    classes = [client.post("/classes/", json={"nom": f"1AM{i + 1}",
                                              "niveau": "moyen", "effectif": 30},
                           headers=entetes).json()["id"]
               for i in range(nb_classes)]

    # Un enseignant ne peut pas couvrir plus de 32 créneaux : dimensionner
    # le corps enseignant sur le volume horaire réel de chaque matière.
    profs = {}
    for nom, _, heures, _ in PROGRAMME:
        nombre = max(1, (heures * nb_classes + 19) // 20)
        profs[nom] = [client.post("/professeurs/", json={
            "nom": f"P{nom}{k}", "prenom": "X", "max_heures_consecutives": 4,
            "matieres_ids": [matieres[nom]]}, headers=entetes).json()["id"]
            for k in range(nombre)]

    edt = client.post("/emplois-du-temps/",
                      json={"nom": "Semaine type", "annee_scolaire": "2025-2026"},
                      headers=entetes).json()["id"]
    return entetes, matieres, classes, profs, edt


def _demande(matieres, classes, profs, **extra):
    cours = []
    for rang, classe in enumerate(classes):
        for nom, _, heures, doubles in PROGRAMME:
            enseignants = profs[nom]
            cours.append({
                "classe_id": classe,
                "matiere_id": matieres[nom],
                "professeur_id": enseignants[rang % len(enseignants)],
                "heures_par_semaine": heures,
                "nb_seances_doubles": doubles,
            })
    return {"cours_requis": cours, "limite_secondes": 20,
            "grille": {"fermetures": [[2, [4, 5, 6]]]}, **extra}


def _attendre(entetes, edt, tache_id, delai=90):
    limite = time.time() + delai
    while time.time() < limite:
        tache = client.get(f"/emplois-du-temps/{edt}/taches/{tache_id}",
                           headers=entetes).json()
        if tache["terminee"]:
            return tache
        time.sleep(0.5)
    raise AssertionError("la tâche ne s'est jamais terminée")


def test_routes_protegees_sans_jeton():
    for methode, url in (("get", "/emplois-du-temps/"), ("get", "/professeurs/"),
                         ("get", "/classes/"), ("get", "/salles/")):
        r = getattr(client, methode)(url)
        assert r.status_code in (401, 403), f"{url} → {r.status_code}"


def test_generation_asynchrone_complete():
    entetes, matieres, classes, profs, edt = _etablissement("async")
    demande = _demande(matieres, classes, profs)

    depart = time.time()
    r = client.post(f"/emplois-du-temps/{edt}/generer", json=demande, headers=entetes)
    assert r.status_code == 202, r.text
    # La mise en file doit rendre la main tout de suite.
    assert time.time() - depart < 5.0
    tache_id = r.json()["id"]

    tache = _attendre(entetes, edt, tache_id)
    assert tache["statut"] == "terminee", tache["message"]
    attendu = sum(h for _, _, h, _ in PROGRAMME) * len(classes)
    assert tache["resultat"]["lecons_planifiees"] == attendu
    assert tache["resultat"]["qualite"]["trous_classes"] == 0

    lecons = client.get(f"/emplois-du-temps/{edt}/lecons", headers=entetes).json()
    assert len(lecons) == attendu


def test_une_seule_generation_a_la_fois():
    entetes, matieres, classes, profs, edt = _etablissement("concurrent")
    demande = _demande(matieres, classes, profs, limite_secondes=30)
    premiere = client.post(f"/emplois-du-temps/{edt}/generer", json=demande,
                           headers=entetes)
    assert premiere.status_code == 202
    seconde = client.post(f"/emplois-du-temps/{edt}/generer", json=demande,
                          headers=entetes)
    assert seconde.status_code == 409
    client.delete(f"/emplois-du-temps/{edt}/taches/{premiere.json()['id']}",
                  headers=entetes)
    _attendre(entetes, edt, premiere.json()["id"])


def test_annulation_interrompt_le_calcul():
    # Une instance jouet atteint l'optimum en moins d'une seconde : il
    # faut un problème que le solveur explore encore pour que
    # l'annulation ait un sens.
    entetes, matieres, classes, profs, edt = _etablissement("annul", nb_classes=14)
    demande = _demande(matieres, classes, profs, limite_secondes=600)
    tache_id = client.post(f"/emplois-du-temps/{edt}/generer", json=demande,
                           headers=entetes).json()["id"]
    time.sleep(4)
    en_cours = client.get(f"/emplois-du-temps/{edt}/taches/{tache_id}",
                          headers=entetes).json()
    assert not en_cours["terminee"], "le solveur a fini avant l'annulation"

    depart = time.time()
    r = client.delete(f"/emplois-du-temps/{edt}/taches/{tache_id}", headers=entetes)
    assert r.status_code == 200, r.text
    tache = _attendre(entetes, edt, tache_id, delai=60)
    assert tache["statut"] == "annulee"
    # L'arrêt doit être immédiat, sans attendre la limite de 600 s.
    assert time.time() - depart < 45


def test_diagnostic_signale_les_donnees_incoherentes():
    entetes, matieres, classes, profs, edt = _etablissement("diag")
    demande = _demande(matieres, classes, profs)
    r = client.post(f"/emplois-du-temps/{edt}/diagnostic", json=demande,
                    headers=entetes)
    assert r.status_code == 200 and r.json()["realisable"]

    # Professeur affecté à une matière qu'il n'enseigne pas.
    mauvais = dict(demande, cours_requis=[{
        "classe_id": classes[0], "matiere_id": matieres["Maths"],
        "professeur_id": profs["Arabe"][0], "heures_par_semaine": 4}])
    r = client.post(f"/emplois-du-temps/{edt}/diagnostic", json=mauvais,
                    headers=entetes)
    assert not r.json()["realisable"]
    assert "n'enseigne pas" in r.json()["erreurs"][0]

    # La génération refuse la demande sans occuper le pool de calcul.
    r = client.post(f"/emplois-du-temps/{edt}/generer", json=mauvais, headers=entetes)
    assert r.status_code == 422
    assert r.json()["detail"]["erreurs"]


def test_cloisonnement_entre_etablissements():
    """Une école ne doit jamais voir l'emploi du temps d'une autre."""
    entetes_a, matieres, classes, profs, edt_a = _etablissement("ecoleA")
    entetes_b, *_ = _etablissement("ecoleB")

    assert client.get(f"/emplois-du-temps/{edt_a}/lecons",
                      headers=entetes_b).status_code == 404
    assert client.post(f"/emplois-du-temps/{edt_a}/generer",
                       json=_demande(matieres, classes, profs),
                       headers=entetes_b).status_code == 404
    # L'école B ne voit que le sien, jamais celui de l'école A.
    visibles = {e["id"] for e in client.get("/emplois-du-temps/",
                                            headers=entetes_b).json()}
    assert edt_a not in visibles


def test_limite_de_calcul_est_plafonnee():
    from app.config import settings
    entetes, matieres, classes, profs, edt = _etablissement("plafond")
    demande = _demande(matieres, classes, profs, limite_secondes=999_999)
    tache_id = client.post(f"/emplois-du-temps/{edt}/generer", json=demande,
                           headers=entetes).json()["id"]
    import json as _json
    from app.database import SessionLocal
    from app.models.task import TacheGeneration
    db = SessionLocal()
    try:
        stockee = _json.loads(db.get(TacheGeneration, tache_id).requete)
        assert stockee["limite_secondes"] == settings.LIMITE_SECONDES_MAX
    finally:
        db.close()
    client.delete(f"/emplois-du-temps/{edt}/taches/{tache_id}", headers=entetes)
    _attendre(entetes, edt, tache_id)


# ══════════════════════════════════════════════════════════════════
#  Jeu de démonstration
# ══════════════════════════════════════════════════════════════════

def test_demonstration_apercu_ne_cree_rien():
    entetes, *_ = _etablissement("demo-apercu")
    apercu = client.get("/demonstration/", headers=entetes).json()
    assert apercu["classes"] > 0 and apercu["professeurs"] > 0
    # L'établissement de test contient déjà des ressources.
    assert apercu["etablissement_deja_peuple"] is True

    vierge = client.post("/auth/inscrire", json={
        "ecole": {"nom": "Vierge", "email": "vierge@test.dz"},
        "admin": {"nom": "A", "prenom": "B", "email": "vierge-admin@test.dz",
                  "mot_de_passe": "motdepasse-solide"}})
    h = {"Authorization": f"Bearer {vierge.json()['access_token']}"}
    assert client.get("/demonstration/", headers=h).json()[
        "etablissement_deja_peuple"] is False
    # L'aperçu n'a rien écrit.
    assert client.get("/matieres/", headers=h).json() == []


def test_demonstration_refuse_decraser_sans_confirmation():
    """Effacer le travail d'un responsable sans le lui demander serait pire
    que de ne rien faire."""
    entetes, matieres, classes, profs, edt = _etablissement("demo-ecrase")
    avant = len(client.get("/matieres/", headers=entetes).json())

    r = client.post("/demonstration/charger", json={}, headers=entetes)
    assert r.status_code == 409
    assert len(client.get("/matieres/", headers=entetes).json()) == avant

    r = client.post("/demonstration/charger", json={"remplacer": True},
                    headers=entetes)
    assert r.status_code == 201, r.text
    apres = client.get("/matieres/", headers=entetes).json()
    assert len(apres) == r.json()["matieres"]
    # Les emplois du temps de l'établissement ont été remplacés eux aussi.
    edts = client.get("/emplois-du-temps/", headers=entetes).json()
    assert [e["id"] for e in edts] == [r.json()["emploi_du_temps_id"]]


def test_demonstration_produit_un_emploi_du_temps_complet():
    """Le jeu doit se générer sans intervention : c'est tout son intérêt."""
    r = client.post("/auth/inscrire", json={
        "ecole": {"nom": "Demo", "email": "demo-gen@test.dz"},
        "admin": {"nom": "A", "prenom": "B", "email": "demo-gen-a@test.dz",
                  "mot_de_passe": "motdepasse-solide"}})
    entetes = {"Authorization": f"Bearer {r.json()['access_token']}"}

    installation = client.post("/demonstration/charger", json={},
                               headers=entetes)
    assert installation.status_code == 201, installation.text
    edt = installation.json()["emploi_du_temps_id"]

    programme = client.get("/demonstration/programme", headers=entetes).json()
    assert sum(c["heures_par_semaine"] for c in programme) == \
        installation.json()["lecons_a_placer"]

    demande = {"cours_requis": programme, "limite_secondes": 60}
    diagnostic = client.post(f"/emplois-du-temps/{edt}/diagnostic",
                             json=demande, headers=entetes).json()
    assert diagnostic["realisable"], diagnostic["erreurs"]

    tache = client.post(f"/emplois-du-temps/{edt}/generer", json=demande,
                        headers=entetes)
    assert tache.status_code == 202
    etat = _attendre(entetes, edt, tache.json()["id"], delai=120)
    assert etat["statut"] == "terminee", etat["message"]
    assert etat["resultat"]["lecons_planifiees"] == \
        installation.json()["lecons_a_placer"]
    assert etat["resultat"]["qualite"]["trous_classes"] == 0

    # Les indisponibilités du jeu doivent être respectées.
    lecons = client.get(f"/emplois-du-temps/{edt}/lecons", headers=entetes).json()
    partages = [p for p in client.get("/professeurs/", headers=entetes).json()
                if p["nom"] == "Cherif"]
    assert partages, "l'enseignant partagé du jeu est absent"
    hors_dispo = [l for l in lecons
                  if l["professeur_id"] == partages[0]["id"]
                  and l["jour"] == "Jeudi" and l["heure_debut"] >= "13:00"]
    assert hors_dispo == [], hors_dispo


def test_demonstration_programme_absent_est_signale():
    r = client.post("/auth/inscrire", json={
        "ecole": {"nom": "Sans demo", "email": "sansdemo@test.dz"},
        "admin": {"nom": "A", "prenom": "B", "email": "sansdemo-a@test.dz",
                  "mot_de_passe": "motdepasse-solide"}})
    entetes = {"Authorization": f"Bearer {r.json()['access_token']}"}
    reponse = client.get("/demonstration/programme", headers=entetes)
    assert reponse.status_code == 409
    assert "démonstration" in reponse.json()["detail"]


if __name__ == "__main__":
    echecs = 0
    for nom, fonction in sorted(globals().items()):
        if not nom.startswith("test_") or not callable(fonction):
            continue
        depart = time.perf_counter()
        try:
            fonction()
            print(f"  ✓ {nom}  ({time.perf_counter() - depart:.1f}s)")
        except Exception as e:
            echecs += 1
            import traceback
            print(f"  ✗ {nom}\n      {e or type(e).__name__}")
            print("      " + traceback.format_exc().replace("\n", "\n      ")[:900])
    if BASE.exists():
        BASE.unlink()
    print(f"\n{'Tous les tests passent.' if not echecs else f'{echecs} échec(s).'}")
    sys.exit(1 if echecs else 0)
