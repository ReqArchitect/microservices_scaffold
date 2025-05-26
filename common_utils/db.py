import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

def get_engine(service_name: str):
    db_url = os.environ.get(f"{service_name.upper()}_DATABASE_URL") or os.environ.get("DATABASE_URL")
    return create_engine(db_url, pool_size=20, max_overflow=0, pool_pre_ping=True)

def get_session(engine):
    return scoped_session(sessionmaker(bind=engine))

def health_check(engine):
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False 