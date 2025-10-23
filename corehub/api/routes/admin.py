"""
Admin control endpoints.

Handles system administration and control functions.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from corehub.db.database import get_db
from corehub.db.models import Flag

router = APIRouter()


@router.post("/pause")
async def toggle_system_pause(
    request: Dict[str, bool],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Toggle system pause flag.
    
    Args:
        request: Request body with paused boolean
        db: Database session dependency
        
    Returns:
        Dict containing current pause status
        
    Raises:
        HTTPException: If request is invalid
    """
    paused = request.get("paused")
    
    if paused is None:
        raise HTTPException(
            status_code=400,
            detail="'paused' field is required"
        )
    
    # Get or create system_paused flag
    flag = db.query(Flag).filter(Flag.key == "system_paused").first()
    
    if not flag:
        flag = Flag(
            key="system_paused",
            value=str(paused).lower(),
            description="System pause flag",
            updated_at=datetime.utcnow()
        )
        db.add(flag)
    else:
        flag.value = str(paused).lower()
        flag.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(flag)
    
    return {
        "system_paused": paused,
        "message": f"System {'paused' if paused else 'resumed'}",
        "timestamp": flag.updated_at.isoformat()
    }


@router.get("/pause")
async def get_system_pause_status(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current system pause status.
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing current pause status
    """
    flag = db.query(Flag).filter(Flag.key == "system_paused").first()
    
    if not flag:
        # Default to not paused if flag doesn't exist
        is_paused = False
    else:
        is_paused = flag.value.lower() == "true"
    
    return {
        "system_paused": is_paused,
        "timestamp": flag.updated_at.isoformat() if flag else datetime.utcnow().isoformat()
    }


@router.get("/flags")
async def list_system_flags(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all system flags.
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing all system flags
    """
    flags = db.query(Flag).all()
    
    return {
        "flags": [
            {
                "key": flag.key,
                "value": flag.value,
                "description": flag.description,
                "updated_at": flag.updated_at.isoformat()
            }
            for flag in flags
        ],
        "total": len(flags)
    }


@router.put("/flags/{flag_key}")
async def update_system_flag(
    flag_key: str,
    request: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a system flag.
    
    Args:
        flag_key: Flag key to update
        request: Request body with new value
        db: Database session dependency
        
    Returns:
        Dict containing updated flag info
        
    Raises:
        HTTPException: If flag not found or invalid request
    """
    new_value = request.get("value")
    description = request.get("description")
    
    if not new_value:
        raise HTTPException(
            status_code=400,
            detail="'value' field is required"
        )
    
    flag = db.query(Flag).filter(Flag.key == flag_key).first()
    
    if not flag:
        raise HTTPException(
            status_code=404,
            detail=f"Flag '{flag_key}' not found"
        )
    
    flag.value = new_value
    if description:
        flag.description = description
    flag.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(flag)
    
    return {
        "key": flag.key,
        "value": flag.value,
        "description": flag.description,
        "updated_at": flag.updated_at.isoformat(),
        "message": f"Flag '{flag_key}' updated successfully"
    }
