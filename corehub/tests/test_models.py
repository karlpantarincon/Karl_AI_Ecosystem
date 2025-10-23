"""
Tests for SQLAlchemy models.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from corehub.db.models import Base, Task, Run, Event, Flag

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_task_model(db_session):
    """Test Task model creation and properties."""
    task = Task(
        id="T-101",
        title="Test task",
        type="dev",
        prio=1,
        status="todo"
    )
    
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    
    assert task.id == "T-101"
    assert task.title == "Test task"
    assert task.type == "dev"
    assert task.prio == 1
    assert task.status == "todo"
    assert task.created_at is not None
    assert task.updated_at is not None
    
    # Test string representation
    assert "T-101" in str(task)
    assert "Test task" in str(task)


def test_run_model(db_session):
    """Test Run model creation and properties."""
    run = Run(
        agent="devagent",
        task_id="T-101",
        status="completed",
        cost_usd=0.25,
        duration_sec=120.0
    )
    
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    
    assert run.agent == "devagent"
    assert run.task_id == "T-101"
    assert run.status == "completed"
    assert run.cost_usd == 0.25
    assert run.duration_sec == 120.0
    assert run.created_at is not None
    
    # Test string representation
    assert "devagent" in str(run)
    assert "completed" in str(run)


def test_event_model(db_session):
    """Test Event model creation and properties."""
    payload = {"task_id": "T-101", "duration": 120}
    event = Event(
        agent="devagent",
        type="task_start",
        payload=payload
    )
    
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.agent == "devagent"
    assert event.type == "task_start"
    assert event.payload == payload
    assert event.created_at is not None
    
    # Test string representation
    assert "task_start" in str(event)
    assert "devagent" in str(event)


def test_flag_model(db_session):
    """Test Flag model creation and properties."""
    flag = Flag(
        key="system_paused",
        value="false",
        description="System pause flag"
    )
    
    db_session.add(flag)
    db_session.commit()
    db_session.refresh(flag)
    
    assert flag.key == "system_paused"
    assert flag.value == "false"
    assert flag.description == "System pause flag"
    assert flag.updated_at is not None
    
    # Test string representation
    assert "system_paused" in str(flag)
    assert "false" in str(flag)


def test_task_model_relationships(db_session):
    """Test Task model with relationships."""
    # Create a task
    task = Task(
        id="T-102",
        title="Related task",
        type="dev",
        prio=1,
        status="todo"
    )
    
    db_session.add(task)
    db_session.commit()
    
    # Create a run for this task
    run = Run(
        agent="devagent",
        task_id="T-102",
        status="completed",
        cost_usd=0.30,
        duration_sec=150.0
    )
    
    db_session.add(run)
    db_session.commit()
    
    # Verify the relationship
    assert run.task_id == task.id


def test_event_model_with_payload(db_session):
    """Test Event model with complex payload."""
    complex_payload = {
        "task_id": "T-103",
        "steps": ["analyze", "implement", "test"],
        "metrics": {
            "lines_added": 50,
            "lines_removed": 10,
            "files_changed": 3
        }
    }
    
    event = Event(
        agent="devagent",
        type="task_complete",
        payload=complex_payload
    )
    
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.payload == complex_payload
    assert event.payload["task_id"] == "T-103"
    assert len(event.payload["steps"]) == 3
    assert event.payload["metrics"]["lines_added"] == 50


def test_model_timestamps(db_session):
    """Test that model timestamps are set correctly."""
    # Create models
    task = Task(
        id="T-104",
        title="Timestamp test",
        type="dev",
        prio=1,
        status="todo"
    )
    
    run = Run(
        agent="devagent",
        task_id="T-104",
        status="started"
    )
    
    event = Event(
        agent="devagent",
        type="test_event"
    )
    
    flag = Flag(
        key="test_flag",
        value="test_value"
    )
    
    # Add to session
    db_session.add_all([task, run, event, flag])
    db_session.commit()
    
    # Check that timestamps are set
    assert task.created_at is not None
    assert task.updated_at is not None
    assert run.created_at is not None
    assert event.created_at is not None
    assert flag.updated_at is not None
    
    # Check that created_at and updated_at are close to now
    now = datetime.utcnow()
    time_diff = abs((now - task.created_at).total_seconds())
    assert time_diff < 5  # Within 5 seconds


def test_model_constraints(db_session):
    """Test model constraints and validations."""
    # Test that required fields are enforced
    with pytest.raises(Exception):  # Should fail due to missing required fields
        task = Task()  # Missing required fields
        db_session.add(task)
        db_session.commit()
    
    # Test that primary keys are unique
    task1 = Task(
        id="T-105",
        title="First task",
        type="dev",
        prio=1,
        status="todo"
    )
    
    task2 = Task(
        id="T-105",  # Same ID
        title="Second task",
        type="dev",
        prio=1,
        status="todo"
    )
    
    db_session.add(task1)
    db_session.commit()
    
    with pytest.raises(Exception):  # Should fail due to duplicate primary key
        db_session.add(task2)
        db_session.commit()
