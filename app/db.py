# app/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération de la chaîne de connexion à la base PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL") 

# Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles ORM
Base = declarative_base()

# Dépendance FastAPI pour gérer la session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
