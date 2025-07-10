# Point d'entrée de l'API FastAPI
from db.database import engine
from db import models
from fastapi import FastAPI
from routes import auth
from routes import profil
from routes import plan
from routes import recettes
from routes import utilisateurs
from routes import personnalisation
from routes import partage
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ou ["*"] en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

app.include_router(utilisateurs.router)

models.Base.metadata.create_all(bind=engine)

app.include_router(profil.router)

app.include_router(partage.router)

app.include_router(plan.router)

app.include_router(recettes.router)

