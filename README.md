# Planner — emplois du temps des CEM et lycées algériens

Un solveur qui propose une grille complète, et une interface où le
responsable garde le dernier mot : il retouche à la main ce qu'il veut,
sans jamais pouvoir produire une grille impossible.

## Structure

| Dossier | Contenu |
|---|---|
| `backend/` | API FastAPI, solveur CP-SAT (OR-Tools), migrations Alembic |
| `app/` | Application Flutter — **une seule base de code** pour le web, Android et iOS |
| `design-system/` | Direction artistique retenue, pour que les écrans à venir s'y conforment |

## Démarrer

```bash
docker compose up --build
```

- l'interface sur <http://localhost:8080>
- l'API et sa documentation sur <http://localhost:8000/docs>

Créez un établissement depuis l'écran de connexion, puis chargez vos
données par classeur Excel (écran **Données**) — ou d'un clic avec le
jeu de démonstration, un CEM complet de 20 divisions.

## Développer

```bash
# API
cd backend && pip install -r requirements.txt
SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))") \
DEBUG=true DATABASE_URL=sqlite:///./planner.db \
  python -m uvicorn app.main:app --reload

# Application
cd app && flutter run -d chrome --dart-define=API_BASE=http://localhost:8000
```

## Tests

```bash
cd backend
python tests/test_solveur.py      # solveur et métriques de qualité
python tests/test_api.py          # API, sécurité, import Excel, retouches
python tests/test_migrations.py   # aller-retour des migrations
cd ../app && flutter analyze
```

## Deux points à connaître avant de modifier

**Le fouj.** Deux cours partageant un `couplage_id` sont donnés en même
temps à deux demi-groupes, par deux enseignants, dans deux salles. La
division n'occupe alors qu'un seul créneau. Toute mesure côté élèves
doit dédoublonner par créneau, sans quoi les trous et les charges sont
faussés.

**Demi-journée contre journée entière.** Un trou est une heure creuse
_entre deux cours de la même demi-journée_ : la pause déjeuner n'en est
pas un. Seul le critère de « journée hachée » raisonne sur la journée
entière. Confondre les deux fait apparaître des trous qui n'existent
pas — c'est arrivé deux fois.

## Langues

Français et arabe, à parité stricte. L'interface suit la langue de
l'appareil et bascule complètement en lecture de droite à gauche.
Ajouter une chaîne, c'est l'ajouter dans `app/lib/l10n/app_fr.arb` **et**
`app_ar.arb` : la compilation échoue sinon.
