"""Point d'entrée de l'API FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .migrations import verifier as verifier_schema
from .routers import (
    auth, teachers, subjects, rooms, classes, schedules, demo, donnees,
    settings as reglages, programme,
)

# Le schéma est versionné par Alembic : on contrôle qu'il est à jour au
# lieu de le créer à la volée. En développement, la migration manquante
# est appliquée automatiquement ; en production, le démarrage échoue
# avec la marche à suivre.
verifier_schema()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="API REST pour la génération automatique d'emplois du temps scolaires.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — liste explicite d'origines. Le joker « * » est incompatible
# avec allow_credentials : les navigateurs rejettent la combinaison, et
# elle ouvrirait l'API à n'importe quel site.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origines_cors,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Enregistrer les routers
app.include_router(auth.router)
app.include_router(teachers.router)
app.include_router(subjects.router)
app.include_router(rooms.router)
app.include_router(classes.router)
app.include_router(schedules.router)
app.include_router(reglages.router)
app.include_router(programme.router)
app.include_router(demo.router)
app.include_router(donnees.router)


@app.get("/", tags=["Santé"])
def racine():
    return {
        "message": "Plateforme Emploi du Temps Scolaire — API opérationnelle",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/sante", tags=["Santé"])
def sante():
    return {"statut": "ok"}
