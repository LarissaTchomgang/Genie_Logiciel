# routes/personnalisation.py
# ────────────────────────────────────────────────────────────────
"""
Personnalisation du plan de repas :
    • GET  /perso/recettes_compatibles/{utilisateur_id}
    • PUT  /perso/plan/{plan_id}/modifier
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db import models
from db.database import get_db

router = APIRouter(prefix="/perso", tags=["Personnalisation"])


# ------------------------------------------------------------------
# 1)  Recettes compatibles avec le profil d’un utilisateur
# ------------------------------------------------------------------
@router.get("/recettes_compatibles/{utilisateur_id}")
def recettes_compatibles(utilisateur_id: int, db: Session = Depends(get_db)):
    """
    Retourne toutes les recettes **cohérentes** avec le profil :
      – régime (végétarien, sans lactose…)
      – allergies  (liste)
      – objectifs  (perte de poids, prise de masse…)

    Filtrage très simple : on vérifie que la colonne `contraintes`
    contient (ILIKE) le régime / l’objectif, et qu’aucun mot‑clef
    d’allergie n’apparaît dans le titre de la recette.
    """
    profil = (
        db.query(models.Profil)
        .filter(models.Profil.utilisateur_id == utilisateur_id)
        .first()
    )
    if profil is None:
        raise HTTPException(404, "Profil introuvable")

    q = db.query(models.Recette)

    # — Régime / objectif
    if profil.regime:
        q = q.filter(models.Recette.contraintes.ilike(f"%{profil.regime}%"))
    if profil.objectifs:
        q = q.filter(models.Recette.contraintes.ilike(f"%{profil.objectifs}%"))

    # — Allergies  (exclusion)
    if profil.allergies:
        # stocké sous forme JSON(string[]) ou CSV ; on boucle
        for allerg in profil.allergies:
            q = q.filter(~models.Recette.titre.ilike(f"%{allerg}%"))

    recettes = q.all()
    return [
        {
            "id": r.id,
            "titre": r.titre,
            "calories": r.calories,
            "contraintes": r.contraintes,
        }
        for r in recettes
    ]


# ------------------------------------------------------------------
# 2)  Remplacer une recette dans un plan
# ------------------------------------------------------------------
@router.put("/plan/{plan_id}/modifier")
def modifier_repas(
    plan_id: int,
    jour: int = Query(..., gt=0, description="Numéro du jour (1 = jour_1)"),
    moment: str = Query(..., regex="^(matin|midi|soir)$"),
    nouvelle_recette_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    """
    • `jour`    : 1, 2, 3 … (correspond à *jour_N* dans la structure)
    • `moment`  : 'matin' | 'midi' | 'soir'
    • `nouvelle_recette_id` : id de la recette choisie
    """

    # ① vérifier l’existence du plan
    plan = db.query(models.Plan).filter_by(id=plan_id).first()
    if plan is None:
        raise HTTPException(404, "Plan introuvable")

    # ② vérifier la nouvelle recette
    new_recette = db.query(models.Recette).filter_by(id=nouvelle_recette_id).first()
    if new_recette is None:
        raise HTTPException(404, "Nouvelle recette introuvable")

    # ③ retrouver le “repas” à modifier
    # ─────────────────────────────────────────────
    # → On suppose que *l’id* du repas encode le jour : id % 1000 == jour
    #   (cette astuce a été employée plus tôt dans tes scripts).
    #   Si tu as maintenant une vraie colonne `jour`
    #   dans la table `repas`, remplace simplement le filtre !
    repas = (
        db.query(models.Repas)
        .filter(models.Repas.plan_id == plan_id)
        .filter(models.Repas.moment == moment)
        .filter(models.Repas.id % 1000 == jour)
        .first()
    )
    if repas is None:
        raise HTTPException(404, "Repas à modifier introuvable")

    # ④ mise à jour
    repas.recette_id = nouvelle_recette_id
    repas.personnalise = True
    db.commit()
    db.refresh(repas)

    return {
        "message": "Repas mis à jour ✅",
        "repas_id": repas.id,
        "nouvelle_recette_id": nouvelle_recette_id,
    }
