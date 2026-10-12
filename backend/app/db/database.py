from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

database_url = settings.DATABASE_URL

# Render/Neon and several managed Postgres providers expose URLs as
# postgresql:// or postgres://. Explicitly select psycopg v3 so production
# does not depend on the legacy psycopg2 driver.
if database_url.startswith("postgres://"):
    database_url = "postgresql+psycopg://" + database_url[len("postgres://"):]
elif database_url.startswith("postgresql://") and "+" not in database_url.split("://", 1)[0]:
    database_url = "postgresql+psycopg://" + database_url[len("postgresql://"):]

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so they register on Base.metadata before create_all.
    # Production uses a fresh managed Postgres database for the initial deploy.
    from app.models import (  # noqa: F401
        user,
        email_model,
        task_model,
        calendar_model,
        note_model,
        chat_model,
        memory_model,
        agent_action,
    )

    Base.metadata.create_all(bind=engine)
