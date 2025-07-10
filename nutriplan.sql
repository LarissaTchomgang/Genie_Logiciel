-- Database: nutriplan

-- DROP DATABASE IF EXISTS nutriplan;

CREATE DATABASE nutriplan
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

		-- Table des utilisateurs
	CREATE TABLE utilisateurs (
	    id SERIAL PRIMARY KEY,
	    nom VARCHAR(100),
	    email VARCHAR(100) UNIQUE NOT NULL,
	    mot_de_passe TEXT NOT NULL
	);

		-- Profil associé à chaque utilisateur
	CREATE TABLE profils (
	    id SERIAL PRIMARY KEY,
	    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
	    regime VARCHAR(100),
	    allergies TEXT[],
	    objectifs TEXT
	);
	
	-- Recettes
	CREATE TABLE recettes (
	    id SERIAL PRIMARY KEY,
	    titre VARCHAR(200),
	    description TEXT,
	    instructions TEXT,
	    calories INTEGER
	);
	
	-- Ingrédients
	CREATE TABLE ingredients (
	    id SERIAL PRIMARY KEY,
	    nom VARCHAR(100),
	    unite VARCHAR(20)
	);
	
	-- Relation N-N entre recettes et ingrédients
	CREATE TABLE recette_ingredients (
	    id SERIAL PRIMARY KEY,
	    recette_id INTEGER REFERENCES recettes(id) ON DELETE CASCADE,
	    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
	    quantite FLOAT
	);
	
	-- Plans de repas
	CREATE TABLE plans (
	    id SERIAL PRIMARY KEY,
	    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
	    date_debut DATE
	);
	
	-- Repas (matin, midi, soir)
	CREATE TABLE repas (
	    id SERIAL PRIMARY KEY,
	    plan_id INTEGER REFERENCES plans(id) ON DELETE CASCADE,
	    moment VARCHAR(20), -- exemple : 'matin', 'midi', 'soir'
	    recette_id INTEGER REFERENCES recettes(id),
	    personnalise BOOLEAN DEFAULT FALSE
	);
	
	-- Liste de courses
	CREATE TABLE liste_courses (
	    id SERIAL PRIMARY KEY,
	    plan_id INTEGER REFERENCES plans(id) ON DELETE CASCADE,
	    ingredient TEXT,
	    quantite FLOAT,
	    unite VARCHAR(20)
	);

	ALTER TABLE recettes ADD COLUMN contraintes TEXT;

	UPDATE recettes
	SET contraintes = 'sans gluten, perte de poids, riche en protéines'
	WHERE id = 1;
	
	UPDATE recettes
	SET contraintes = 'riche en protéines, riche en fibres, sans gluten'
	WHERE id = 2;
	
	UPDATE recettes
	SET contraintes = 'sans lactose, sans arachides, riche en légumes'
	WHERE id = 3;
	
	UPDATE recettes
	SET contraintes = 'végétarien, diabétique, faible en glucides'
	WHERE id = 4;

	UPDATE recettes
	SET contraintes = 'riche en légumes, diabétique, faible en glucides'
	WHERE id = 15;
	


	SELECT * FROM ingredients
	SELECT * FROM recettes
	SELECT * FROM utilisateurs
	SELECT * FROM profils
	SELECT * FROM recette_ingredients
	SELECT * FROM repas
	SELECT * FROM liste_courses
	SELECT * FROM plans 