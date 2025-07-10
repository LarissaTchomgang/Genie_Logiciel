# routes/plan.py
# ───────────────────────────────────────────────────────────
from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import models
from db.database import get_db
from services.local_planner import generer_plan_local

router = APIRouter(prefix="/plan", tags=["Planification"])


# ───────────────────────────────────────────────────────────
# 1) Génération d'un plan local (filtré)
# ───────────────────────────────────────────────────────────
@router.post("/planifier_local/{utilisateur_id}")
def planifier_local(
    utilisateur_id: int,
    jours: int = 3,
    db: Session = Depends(get_db),
):
    # génère la structure (ne touche pas encore à la BD)
    structure = generer_plan_local(db=db, utilisateur_id=utilisateur_id, jours=jours)

    # ── Création du plan ───────────────────────────────────
    plan = models.Plan(utilisateur_id=utilisateur_id, date_debut=date.today())
    db.add(plan)
    db.commit()
    db.refresh(plan)

    total_ing = defaultdict(lambda: [0.0, ""])  # nom → [qte cumulée, unité]

    # ── Repas + cumul ingrédients ─────────────────────────
    for jour, moments in structure.items():
        for moment, titre in moments.items():
            recette = (
                db.query(models.Recette)
                .filter(models.Recette.titre == titre)
                .first()
            )
            if not recette:
                continue

            # Insère le repas
            db.add(
                models.Repas(
                    plan_id=plan.id,
                    moment=moment,
                    recette_id=recette.id,
                    personnalise=False,
                )
            )

            # Cumul ingrédients pour la liste de courses
            for assoc in recette.ingredients:
                nom = assoc.ingredient.nom
                total_ing[nom][0] += assoc.quantite or 1.0
                total_ing[nom][1] = assoc.ingredient.unite or ""

    db.commit()

    # ── ListeCourses ──────────────────────────────────────
    for nom, (qte, unite) in total_ing.items():
        db.add(
            models.ListeCourses(
                plan_id=plan.id,
                ingredient=nom,
                quantite=qte,
                unite=unite,
            )
        )
    db.commit()

    return {
        "message": f"Plan local de {jours} jour(s) généré ✅",
        "plan_id": plan.id,
        "aperçu": structure,
    }


# ───────────────────────────────────────────────────────────
# 2) Récupération de la liste de courses
# ───────────────────────────────────────────────────────────
@router.get("/courses/{plan_id}")
def get_liste_courses(plan_id: int, db: Session = Depends(get_db)):
    items = db.query(models.ListeCourses).filter_by(plan_id=plan_id).all()
    if not items:
        raise HTTPException(404, "Aucune liste de courses pour ce plan")

    return [
        {
            "id": it.id,
            "ingredient": it.ingredient,
            "quantite": it.quantite,
            "unite": it.unite,
        }
        for it in items
    ]
