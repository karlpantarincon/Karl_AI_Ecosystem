"""
Health check endpoints.

Provides system health status and database connectivity checks.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from corehub.db.database import get_db, check_db_connection, get_db_info

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dict containing system status and timestamp
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "CoreHub API",
        "version": "0.1.0"
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with database status.
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing detailed system status
        
    Raises:
        HTTPException: If database is not healthy
    """
    # Check database connection
    db_healthy = check_db_connection()
    db_info = get_db_info()
    
    if not db_healthy:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "CoreHub API",
        "version": "0.1.0",
        "database": db_info,
        "components": {
            "api": "healthy",
            "database": "healthy" if db_healthy else "unhealthy",
            "scheduler": "healthy",  # TODO: Add actual scheduler health check
        }
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/container orchestration.
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing readiness status
    """
    # Check if all required services are ready
    db_ready = check_db_connection()
    
    if not db_ready:
        raise HTTPException(
            status_code=503,
            detail="Service not ready - database unavailable"
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "ready": True
    }
