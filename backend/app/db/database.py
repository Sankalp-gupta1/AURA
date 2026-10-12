from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


database_url = settings.DATABASE_URL

# Render provides postgresql:// URLs. SQLAlchemy + psycopg v3 uses the
# explicit postgresql+psycopg:// driver form.
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
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
    # Import models so they register on Base.metadata before create_all
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
