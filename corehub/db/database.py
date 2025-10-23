"""
Database configuration and session management.

This module provides:
- Database engine configuration
- Session factory
- Connection utilities
- Database health checks
"""

import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .models import Base

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "POSTGRES_URL", 
    "sqlite:///./karl_ecosystem.db"
)

# Create engine with appropriate configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db_info() -> dict:
    """
    Get database connection information.
    
    Returns:
        dict: Database connection info
    """
    try:
        with engine.connect() as connection:
            # Para SQLite usar sqlite_version()
            if "sqlite" in DATABASE_URL:
                result = connection.execute(text("SELECT sqlite_version()"))
            else:
                result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
        return {
            "connected": True,
            "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "unknown",
            "version": version,
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }
