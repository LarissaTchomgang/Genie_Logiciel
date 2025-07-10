from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import schemas, models
from db.database import get_db
from utils.security import get_current_user
from fastapi.security import OAuth2PasswordBearer
from utils.security import decode_token
from fastapi import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/profil", tags=["Profil Utilisateur"])

# 🔐 Récupérer le profil de l'utilisateur connecté
@router.get("/{utilisateur_id}", response_model=schemas.ProfilRead)
def get_profil(utilisateur_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Vérifie l'identité
    payload = decode_token(token)
    if int(payload.get("sub")) != utilisateur_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    profil = db.query(models.Profil).filter(models.Profil.utilisateur_id == utilisateur_id).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return profil


# 🔐 Créer ou mettre à jour automatiquement le profil
@router.post("/", response_model=schemas.ProfilRead)
def create_or_update_profil(
    profil_data: schemas.ProfilCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    profil = db.query(models.Profil).filter(models.Profil.utilisateur_id == current_user.id).first()

    if profil:
        # Mise à jour
        for key, value in profil_data.dict(exclude_unset=True).items():
            setattr(profil, key, value)
        db.commit()
        db.refresh(profil)
        return profil

    # Création
    new_profil = models.Profil(utilisateur_id=current_user.id, **profil_data.dict())
    db.add(new_profil)
    db.commit()
    db.refresh(new_profil)
    return new_profil


# 🔄 Modifier le profil (alternative explicite avec PUT)
@router.put("/", response_model=schemas.ProfilRead)
def update_profil(
    profil_data: schemas.ProfilBase,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    profil = db.query(models.Profil).filter(models.Profil.utilisateur_id == current_user.id).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil introuvable")

    for key, value in profil_data.dict(exclude_unset=True).items():
        setattr(profil, key, value)

    db.commit()
    db.refresh(profil)
    return profil
