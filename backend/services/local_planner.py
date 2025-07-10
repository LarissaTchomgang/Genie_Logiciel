# services/local_planner.py
# ───────────────────────────────────────────────────────────
"""
Génère localement un plan de repas filtré selon le profil
(utilise uniquement la base PostgreSQL, pas d’IA).
Retourne un dict :
{
    "jour_1": {"matin": "...", "midi": "...", "soir": "..."},
    ...
}
"""

from __future__ import annotations
from datetime import date
from collections import defaultdict
import random
from typing import Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from db import models


# ───────────────────────────────────────────────────────────
def _recettes_compatibles(db: Session, profil: models.Profil) -> list[models.Recette]:
    """
    Filtre les recettes qui respectent toutes les contraintes du profil.
    Les contraintes sont stockées en minuscule et séparées par virgule.
    """
    contraintes_user = set()

    if profil.regime and profil.regime.lower() != "aucun":
        contraintes_user.add(profil.regime.lower())

    if profil.objectifs and profil.objectifs.lower() != "aucun":
        contraintes_user.add(profil.objectifs.lower())

    if profil.allergies:
        # allergies est stocké JSON ou CSV → on normalise
        if isinstance(profil.allergies, list):
            contraintes_user.update(a.lower() for a in profil.allergies)
        else:
            contraintes_user.update(a.strip().lower() for a in profil.allergies.split(","))

    print(f"🔍 Contraintes utilisateur : {contraintes_user}")

    recettes_ok = []
    for r in db.query(models.Recette).all():
        if not r.contraintes:
            continue                      # aucune contrainte → on ignore
        contraintes_r = set(c.strip().lower() for c in r.contraintes.split(","))
        if contraintes_user.issubset(contraintes_r):
            recettes_ok.append(r)

    print(f"✅ Recettes compatibles trouvées : {len(recettes_ok)}")
    return recettes_ok


# ───────────────────────────────────────────────────────────
def generer_plan_local(
    db: Session,
    utilisateur_id: int,
    jours: int = 3,
) -> Dict[str, Dict[str, str]]:
    """
    Retourne la structure complète (sans insertion en BD).
    """
    utilisateur = db.query(models.Utilisateur).get(utilisateur_id)
    if not utilisateur:
        raise HTTPException(404, "Utilisateur introuvable")

    profil = db.query(models.Profil).filter_by(utilisateur_id=utilisateur_id).first()
    if not profil:
        raise HTTPException(404, "Profil introuvable")

    recettes = _recettes_compatibles(db, profil)
    if not recettes:
        raise HTTPException(
            400,
            "Aucune recette compatible avec les contraintes de l'utilisateur",
        )

    # Mélange pour varier
    random.shuffle(recettes)

    structure: Dict[str, Dict[str, str]] = {}
    moments = ["matin", "midi", "soir"]
    idx = 0

    for j in range(1, jours + 1):
        jour_key = f"jour_{j}"
        structure[jour_key] = {}
        for moment in moments:
            # boucle circulaire sur la liste mélangée
            if idx >= len(recettes):
                idx = 0
                random.shuffle(recettes)
            structure[jour_key][moment] = recettes[idx].titre
            idx += 1

    return structure
