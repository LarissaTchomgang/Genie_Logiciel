# Schémas Pydantic
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date


# ----------- Utilisateur -----------

class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurRead(UtilisateurBase):
    id: int

    class Config:
        from_attributes = True


# ----------- Profil -----------

class ProfilBase(BaseModel):
    regime: Optional[str] = None
    allergies: Optional[List[str]] = []
    objectifs: Optional[str] = None

class ProfilCreate(ProfilBase):
    pass

class ProfilRead(ProfilBase):
    id: int
    utilisateur_id: int

    class Config:
        from_attributes = True


# ----------- Ingrédient -----------

class IngrédientBase(BaseModel):
    nom: str
    unite: str

class IngrédientCreate(IngrédientBase):
    pass

class IngrédientRead(IngrédientBase):
    id: int

    class Config:
        from_attributes = True


# ----------- Recette -----------

class RecetteBase(BaseModel):
    titre: str
    description: str
    instructions: str
    calories: int
    contraintes: Optional[str] 

class RecetteCreate(RecetteBase):
    pass

class RecetteRead(RecetteBase):
    id: int

    class Config:
        from_attributes = True


# ----------- RecetteIngredient -----------

class RecetteIngredientBase(BaseModel):
    recette_id: int
    ingredient_id: int
    quantite: float

class RecetteIngredientCreate(RecetteIngredientBase):
    pass

class RecetteIngredientRead(RecetteIngredientBase):
    id: int

    class Config:
        from_attributes = True


# ----------- Plan -----------

class PlanBase(BaseModel):
    date_debut: date

class PlanCreate(PlanBase):
    utilisateur_id: int

class PlanRead(PlanBase):
    id: int
    utilisateur_id: int

    class Config:
        from_attributes = True


# ----------- Repas -----------

class RepasBase(BaseModel):
    moment: str  # matin, midi, soir
    recette_id: int
    personnalise: Optional[bool] = False

class RepasCreate(RepasBase):
    plan_id: int

class RepasRead(RepasBase):
    id: int
    plan_id: int

    class Config:
        from_attributes = True


# ----------- ListeCourses -----------

class ListeCoursesBase(BaseModel):
    ingredient: str
    quantite: float
    unite: str

class ListeCoursesCreate(ListeCoursesBase):
    plan_id: int

class ListeCoursesRead(ListeCoursesBase):
    id: int
    plan_id: int

    class Config:
        from_attributes = True


# ----------- Authentification -----------

class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class Token(BaseModel):
    access_token: str
    token_type: str


class IngredientDetail(BaseModel):
    nom: str
    quantite: float
    unite: str

class RecetteWithIngredients(RecetteRead):
    instructions: str
    ingredients: List[IngredientDetail]
