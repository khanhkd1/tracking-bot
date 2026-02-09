import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("POSTGRES_USER", "user")
db_password = os.getenv("POSTGRES_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "db")
db_name = os.getenv("POSTGRES_DB", "tracking_bot_db")

# Allow overriding via DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
