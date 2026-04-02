"""Database configuration for ThrivePay.

This module defines a SQLAlchemy engine and a session factory.  By default the
database uses SQLite (`thrivepay.db` in the project root).  To use a different
database (e.g. PostgreSQL), set the environment variable `DATABASE_URL` before
starting the application.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./thrivepay.db")

# `check_same_thread=False` is required only for SQLite.  It allows the
# SQLAlchemy session to be used in an async context.  For PostgreSQL or other
# databases this parameter can be omitted.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db() -> None:
    """Create database tables based on the SQLAlchemy models.

    This function should be called on application startup.  It will import
    the models module to ensure that all SQLAlchemy model classes are
    registered on the `Base` metadata, then create any missing tables.
    """
    # Import inside the function to avoid circular imports.  Using a relative
    # import allows Python to resolve the package correctly when running
    # `uvicorn app.main:app`.
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)