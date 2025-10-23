"""
Event logging endpoints.

Handles system event logging and retrieval.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from corehub.db.database import get_db
from corehub.db.models import Event

router = APIRouter()


@router.post("/log")
async def log_event(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Log a system event.
    
    Args:
        request: Event data with agent, type, and optional payload
        db: Database session dependency
        
    Returns:
        Dict containing event ID and timestamp
        
    Raises:
        HTTPException: If required fields are missing
    """
    agent = request.get("agent")
    event_type = request.get("type")
    payload = request.get("payload")
    
    if not event_type:
        raise HTTPException(
            status_code=400,
            detail="Event type is required"
        )
    
    # Create event record
    event = Event(
        agent=agent,
        type=event_type,
        payload=payload,
        created_at=datetime.utcnow()
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return {
        "id": event.id,
        "created_at": event.created_at.isoformat(),
        "message": "Event logged successfully"
    }


@router.get("/")
async def list_events(
    agent: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List events with optional filters.
    
    Args:
        agent: Filter by agent name
        event_type: Filter by event type
        limit: Maximum number of events to return
        offset: Number of events to skip
        db: Database session dependency
        
    Returns:
        Dict containing list of events and pagination info
    """
    query = db.query(Event)
    
    if agent:
        query = query.filter(Event.agent == agent)
    
    if event_type:
        query = query.filter(Event.type == event_type)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    events = query.order_by(Event.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "events": [
            {
                "id": event.id,
                "agent": event.agent,
                "type": event.type,
                "payload": event.payload,
                "created_at": event.created_at.isoformat()
            }
            for event in events
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{event_id}")
async def get_event(
    event_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get specific event by ID.
    
    Args:
        event_id: Event identifier
        db: Database session dependency
        
    Returns:
        Dict containing event details
        
    Raises:
        HTTPException: If event not found
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found"
        )
    
    return {
        "id": event.id,
        "agent": event.agent,
        "type": event.type,
        "payload": event.payload,
        "created_at": event.created_at.isoformat()
    }
