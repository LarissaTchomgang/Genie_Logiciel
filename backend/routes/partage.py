# Routes de partage
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import models, schemas
from db.database import get_db
import uuid

router = APIRouter(prefix="/partage", tags=["Partage"])

@router.post("/liste/{plan_id}")
def generer_lien_partage(plan_id: int, db: Session = Depends(get_db)):
    token = str(uuid.uuid4())
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, detail="Plan introuvable")
    
    # Ici, tu peux enregistrer le token dans une table dédiée si tu veux qu’il persiste
    return {"url": f"http://localhost:3000/partage/liste/{token}"}

# Exemple de route GET
@router.get("/liste_courses/{plan_id}")
def get_liste_courses(plan_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(models.ListeCourses)
        .filter(models.ListeCourses.plan_id == plan_id)
        .all()
    )
    return [                # ← soit on renvoie la liste directement…
        {
            "id": it.id,
            "ingredient": it.ingredient,
            "quantite": it.quantite,
            "unite": it.unite,
        }
        for it in items
    ]
    # ou bien:  return {"liste": [...]}  ← si tu préfères l’envelopper

