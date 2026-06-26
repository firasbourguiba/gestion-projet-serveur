"""Connexion à la base SQLite et gestion des sessions SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# check_same_thread=False est nécessaire car FastAPI peut utiliser plusieurs
# threads alors que SQLite n'autorise par défaut qu'un seul thread par connexion.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dépendance FastAPI fournissant une session DB et la fermant après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
