# Routes pour les recettes
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from db import models
from db import schemas
from db.database import get_db
from db.models import Recette
from db.schemas import RecetteCreate, RecetteRead

router = APIRouter(prefix="/recettes", tags=["Recettes"])

# 1️⃣ GET - Liste toutes les recettes
@router.get("/", response_model=list[RecetteRead])
def get_all_recettes(db: Session = Depends(get_db)):
    return db.query(Recette).all()

# 2️⃣ POST - Ajouter une nouvelle recette
@router.post("/", response_model=RecetteRead)
def create_recette(recette: RecetteCreate, db: Session = Depends(get_db)):
    new_recette = Recette(**recette.dict())
    db.add(new_recette)
    db.commit()
    db.refresh(new_recette)
    return new_recette

# 3️⃣ GET - Rechercher par contraintes (sans gluten, végétarien, etc)
@router.get("/{recette_id}", response_model=schemas.RecetteWithIngredients)
def get_recette_by_id(recette_id: int, db: Session = Depends(get_db)):
    recette = db.query(models.Recette).filter(models.Recette.id == recette_id).first()
    if not recette:
        raise HTTPException(404, detail="Recette non trouvée")

    ingredients = [
        {
            "nom": db_ing.ingredient.nom,
            "quantite": db_ing.quantite,
            "unite": db_ing.ingredient.unite
        }
        for db_ing in recette.ingredients
    ]

    return {
        **schemas.RecetteRead.from_orm(recette).dict(),
        "ingredients": ingredients
    }

@router.get("/{recette_id}")
def get_recette_detail(recette_id: int, db: Session = Depends(get_db)):
    recette = db.query(models.Recette).filter(models.Recette.id == recette_id).first()
    if not recette:
        raise HTTPException(404, "Recette introuvable")

    # Récupération des ingrédients liés
    ingredients = db.query(models.RecetteIngredient).filter(
        models.RecetteIngredient.recette_id == recette_id
    ).all()

    return {
        "id": recette.id,
        "titre": recette.titre,
        "description": recette.description,
        "instructions": recette.instructions,
        "calories": recette.calories,
        "contraintes": recette.contraintes,
        "ingredients": [
            {
                "nom": ingr.ingredient.nom,
                "quantite": ingr.quantite,
                "unite": ingr.ingredient.unite
            }
            for ingr in ingredients
        ]
    }


# 4️⃣ DELETE - Supprimer une recette par ID
@router.delete("/{recette_id}")
def delete_recette(recette_id: int, db: Session = Depends(get_db)):
    recette = db.query(Recette).filter(Recette.id == recette_id).first()
    if not recette:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
    db.delete(recette)
    db.commit()
    return {"message": "Recette supprimée"}
