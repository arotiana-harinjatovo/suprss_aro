# app/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Charger les variables d'environnement depuis .env
load_dotenv()

# Lire l'URL de la base de données depuis .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Créer l'engine SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de classe pour les modèles
Base = declarative_base()

# Fonction pour obtenir une session DB dans FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
