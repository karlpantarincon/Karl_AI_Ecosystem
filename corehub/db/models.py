"""
SQLAlchemy models for CoreHub database.

This module defines all database models:
- Task: Kanban tasks
- Run: Agent execution runs
- Event: System events and logs
- Flag: System flags and toggles
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    Index,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Task(Base):
    """Kanban task model."""
    
    __tablename__ = "tasks"
    
    id = Column(String(50), primary_key=True)  # e.g., "T-101"
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # "dev", "ops", "test"
    prio = Column(Integer, nullable=False)  # 1=highest, 5=lowest
    status = Column(String(50), nullable=False, default="todo")  # todo, in_progress, done, blocked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_type', 'type'),
        Index('idx_task_prio', 'prio'),
        Index('idx_task_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Task(id='{self.id}', title='{self.title}', status='{self.status}')>"


class Run(Base):
    """Agent execution run model."""
    
    __tablename__ = "runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=False)  # "devagent", "testagent", etc.
    task_id = Column(String(50), nullable=True)  # FK to Task.id
    status = Column(String(50), nullable=False)  # "started", "completed", "failed"
    cost_usd = Column(Float, default=0.0)
    duration_sec = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_run_agent', 'agent'),
        Index('idx_run_status', 'status'),
        Index('idx_run_task', 'task_id'),
        Index('idx_run_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Run(id={self.id}, agent='{self.agent}', status='{self.status}')>"


class Event(Base):
    """System event and log model."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=True)  # null for system events
    type = Column(String(100), nullable=False)  # "task_start", "health_check", etc.
    payload = Column(JSON, nullable=True)  # Additional event data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_event_agent', 'agent'),
        Index('idx_event_type', 'type'),
        Index('idx_event_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type='{self.type}', agent='{self.agent}')>"


class Flag(Base):
    """System flags and toggles model."""
    
    __tablename__ = "flags"
    
    key = Column(String(100), primary_key=True)  # "system_paused", "maintenance_mode"
    value = Column(String(255), nullable=False)  # "true", "false", or other values
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Flag(key='{self.key}', value='{self.value}')>"
