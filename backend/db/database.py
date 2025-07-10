# Connexion à la base de données
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Connexion directe à PostgreSQL
DATABASE_URL = "postgresql://postgres:lari1234@localhost:5432/nutriplan"
# Remplace "motdepasse" si nécessaire

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Fonction utilitaire pour obtenir une session de DB dans les routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
