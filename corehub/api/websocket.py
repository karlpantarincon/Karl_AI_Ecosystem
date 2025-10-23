"""
WebSocket endpoints for real-time dashboard updates.

Provides real-time data streaming for React frontend.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from corehub.db.database import get_db
from corehub.db.models import Task, Run, Event

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections by room
        self.active_connections: Dict[str, List[WebSocket]] = {
            "dashboard": [],
            "logs": [],
            "metrics": []
        }
    
    async def connect(self, websocket: WebSocket, room: str = "dashboard"):
        """Connect a WebSocket to a specific room."""
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        logger.info(f"WebSocket connected to room: {room}")
    
    def disconnect(self, websocket: WebSocket, room: str = "dashboard"):
        """Disconnect a WebSocket from a room."""
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
            logger.info(f"WebSocket disconnected from room: {room}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_room(self, message: str, room: str):
        """Broadcast a message to all connections in a room."""
        if room not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[room]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to room {room}: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections[room].remove(connection)
    
    async def broadcast_to_all(self, message: str):
        """Broadcast a message to all connections."""
        for room in self.active_connections:
            await self.broadcast_to_room(message, room)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard real-time updates."""
    await manager.connect(websocket, "dashboard")
    
    try:
        # Send initial dashboard data
        initial_data = await get_dashboard_snapshot()
        await manager.send_personal_message(json.dumps(initial_data), websocket)
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for client messages (heartbeat, etc.)
                data = await websocket.receive_text()
                
                # Handle client requests
                if data == "ping":
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                elif data == "refresh":
                    # Send updated dashboard data
                    dashboard_data = await get_dashboard_snapshot()
                    await manager.send_personal_message(json.dumps(dashboard_data), websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in dashboard WebSocket: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "dashboard")


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming."""
    await manager.connect(websocket, "logs")
    
    try:
        # Send recent logs
        recent_logs = await get_recent_logs()
        await manager.send_personal_message(json.dumps({
            "type": "logs",
            "data": recent_logs
        }), websocket)
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in logs WebSocket: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "logs")


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics updates."""
    await manager.connect(websocket, "metrics")
    
    try:
        # Send initial metrics
        initial_metrics = await get_realtime_metrics()
        await manager.send_personal_message(json.dumps(initial_metrics), websocket)
        
        # Send periodic metrics updates
        while True:
            try:
                # Wait for client messages
                data = await websocket.receive_text()
                
                if data == "ping":
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                elif data == "update":
                    # Send updated metrics
                    metrics_data = await get_realtime_metrics()
                    await manager.send_personal_message(json.dumps(metrics_data), websocket)
                
                # Send automatic updates every 30 seconds
                await asyncio.sleep(30)
                metrics_data = await get_realtime_metrics()
                await manager.send_personal_message(json.dumps(metrics_data), websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in metrics WebSocket: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "metrics")


async def get_dashboard_snapshot():
    """Get current dashboard snapshot for WebSocket."""
    try:
        db = next(get_db())
        
        # Get basic stats
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == "done").count()
        in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
        
        # Get recent activity
        recent_runs = db.query(Run).order_by(Run.created_at.desc()).limit(5).all()
        recent_events = db.query(Event).order_by(Event.created_at.desc()).limit(10).all()
        
        # Format recent runs
        runs_data = []
        for run in recent_runs:
            runs_data.append({
                "id": run.id,
                "agent": run.agent,
                "status": run.status,
                "created_at": run.created_at.isoformat(),
                "duration": run.duration_seconds if run.duration_seconds else 0
            })
        
        # Format recent events
        events_data = []
        for event in recent_events:
            events_data.append({
                "id": event.id,
                "agent": event.agent,
                "type": event.type,
                "description": event.description,
                "created_at": event.created_at.isoformat()
            })
        
        db.close()
        
        return {
            "type": "dashboard_snapshot",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "in_progress": in_progress_tasks,
                    "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                "recent_runs": runs_data,
                "recent_events": events_data,
                "system_status": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard snapshot: {e}")
        return {
            "type": "dashboard_snapshot",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


async def get_recent_logs():
    """Get recent logs for WebSocket streaming."""
    try:
        db = next(get_db())
        
        # Get recent events
        recent_events = db.query(Event).order_by(Event.created_at.desc()).limit(50).all()
        
        logs_data = []
        for event in recent_events:
            logs_data.append({
                "id": event.id,
                "timestamp": event.created_at.isoformat(),
                "level": event.type,
                "agent": event.agent,
                "message": event.description,
                "data": event.data if event.data else {}
            })
        
        db.close()
        
        return {
            "type": "logs",
            "timestamp": datetime.utcnow().isoformat(),
            "data": logs_data
        }
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        return {
            "type": "logs",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


async def get_realtime_metrics():
    """Get real-time metrics for WebSocket streaming."""
    try:
        db = next(get_db())
        
        # Get metrics for last hour
        from datetime import timedelta
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Task metrics
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == "done").count()
        
        # Run metrics
        recent_runs = db.query(Run).filter(Run.created_at >= hour_ago).all()
        successful_runs = sum(1 for run in recent_runs if run.status == "completed")
        
        # Calculate metrics
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        success_rate = (successful_runs / len(recent_runs) * 100) if recent_runs else 0
        
        db.close()
        
        return {
            "type": "metrics",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_completion_rate": round(completion_rate, 2),
                "run_success_rate": round(success_rate, 2),
                "total_tasks": total_tasks,
                "recent_runs": len(recent_runs),
                "system_load": "low",
                "active_agents": 1
            }
        }
    except Exception as e:
        logger.error(f"Error getting realtime metrics: {e}")
        return {
            "type": "metrics",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# Functions to broadcast updates from other parts of the system
async def broadcast_task_update(task_data: dict):
    """Broadcast task updates to dashboard connections."""
    message = {
        "type": "task_update",
        "timestamp": datetime.utcnow().isoformat(),
        "data": task_data
    }
    await manager.broadcast_to_room(json.dumps(message), "dashboard")


async def broadcast_new_log(log_data: dict):
    """Broadcast new log entries to log connections."""
    message = {
        "type": "new_log",
        "timestamp": datetime.utcnow().isoformat(),
        "data": log_data
    }
    await manager.broadcast_to_room(json.dumps(message), "logs")


async def broadcast_metrics_update(metrics_data: dict):
    """Broadcast metrics updates to metrics connections."""
    message = {
        "type": "metrics_update",
        "timestamp": datetime.utcnow().isoformat(),
        "data": metrics_data
    }
    await manager.broadcast_to_room(json.dumps(message), "metrics")


async def broadcast_system_alert(alert_data: dict):
    """Broadcast system alerts to all connections."""
    message = {
        "type": "system_alert",
        "timestamp": datetime.utcnow().isoformat(),
        "data": alert_data
    }
    await manager.broadcast_to_all(json.dumps(message))
