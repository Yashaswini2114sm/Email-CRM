from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Engine is the connection to the database
engine = create_engine(settings.DATABASE_URL)

# SessionLocal is a factory that creates new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency that provides a database session to each request.
    The 'yield' ensures the session is always closed after the request,
    even if an error occurs (like a try/finally block).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
