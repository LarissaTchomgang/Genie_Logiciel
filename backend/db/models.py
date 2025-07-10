# Modèles SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from db.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    email = Column(String(100), unique=True, nullable=False)
    mot_de_passe = Column(Text, nullable=False)

    profil = relationship("Profil", back_populates="utilisateur", uselist=False)
    plans = relationship("Plan", back_populates="utilisateur")


class Profil(Base):
    __tablename__ = "profils"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    regime = Column(String(100))
    allergies = Column(Text)  # sous forme CSV ou JSON
    objectifs = Column(Text)

    utilisateur = relationship("Utilisateur", back_populates="profil")


class Recette(Base):
    __tablename__ = "recettes"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200))
    description = Column(Text)
    instructions = Column(Text)
    calories = Column(Integer)
    contraintes = Column(Text)  # ✅ Nouveau champ : pour tags comme "sans gluten, végétarien"

    ingredients = relationship("RecetteIngredient", back_populates="recette")


class Ingrédient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    unite = Column(String(20))

    recettes = relationship("RecetteIngredient", back_populates="ingredient")


class RecetteIngredient(Base):
    __tablename__ = "recette_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recette_id = Column(Integer, ForeignKey("recettes.id", ondelete="CASCADE"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantite = Column(Float)

    recette = relationship("Recette", back_populates="ingredients")
    ingredient = relationship("Ingrédient", back_populates="recettes")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    date_debut = Column(Date)

    utilisateur = relationship("Utilisateur", back_populates="plans")
    repas = relationship("Repas", back_populates="plan")
    liste_courses = relationship("ListeCourses", back_populates="plan")


class Repas(Base):
    __tablename__ = "repas"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"))
    moment = Column(String(20))  # matin, midi, soir
    recette_id = Column(Integer, ForeignKey("recettes.id"))
    personnalise = Column(Boolean, default=False)

    plan = relationship("Plan", back_populates="repas")
    recette = relationship("Recette")


class ListeCourses(Base):
    __tablename__ = "liste_courses"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"))
    ingredient = Column(Text)
    quantite = Column(Float)
    unite = Column(String(20))

    plan = relationship("Plan", back_populates="liste_courses")
