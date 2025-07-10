# Routes d'authentification
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import schemas, models
from db.database import get_db
from utils import security
from db.schemas import UserLogin, Token
from db.models import Profil

router = APIRouter(prefix="/auth", tags=["Authentification"])


# ----- INSCRIPTION -----
@router.post("/register", response_model=schemas.UtilisateurRead)
def register(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    # Vérifie si l'email existe déjà
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.email == utilisateur.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")

    # Hachage du mot de passe
    hashed_password = security.hash_mot_de_passe(utilisateur.mot_de_passe)

    new_user = models.Utilisateur(
        nom=utilisateur.nom,
        email=utilisateur.email,
        mot_de_passe=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ----- CONNEXION -----
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Email incorrect")

    if not security.verify_password(user.mot_de_passe, db_user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    access_token = security.create_access_token({"sub": str(db_user.id)})

     # ✅ Vérifier si un profil existe
    profil = db.query(Profil).filter(Profil.utilisateur_id == db_user.id).first()
    profil_complet = profil is not None

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profil_complet": profil_complet
    }
    #return {"access_token": access_token, "token_type": "bearer"}

