# routes/utilisateur.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from db.database import get_db
from typing import List

router = APIRouter(tags=["Utilisateurs"])


@router.get("/utilisateurs/{utilisateur_id}/liste-courses", response_model=List[schemas.ListeCoursesRead])
def get_liste_courses(utilisateur_id: int, db: Session = Depends(get_db)):
    plans = db.query(models.Plan).filter(models.Plan.utilisateur_id == utilisateur_id).all()
    if not plans:
        return []

    dernier_plan = sorted(plans, key=lambda p: p.date_debut)[-1]
    return db.query(models.ListeCourses).filter(models.ListeCourses.plan_id == dernier_plan.id).all()
