"""
CoreHub API client for DevAgent.

This module provides HTTP client functionality to interact with CoreHub API.
"""

import asyncio
from typing import Dict, Any, Optional

import httpx
from loguru import logger


class CoreHubClient:
    """HTTP client for CoreHub API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize CoreHub client.
        
        Args:
            base_url: Base URL of CoreHub API
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
    
    async def is_system_paused(self) -> bool:
        """
        Check if system is paused.
        
        Returns:
            True if system is paused, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/admin/pause")
            response.raise_for_status()
            data = response.json()
            return data.get("system_paused", False)
        except Exception as e:
            logger.error(f"Failed to check system pause status: {e}")
            return False
    
    async def get_next_task(self, agent: str) -> Optional[Dict[str, Any]]:
        """
        Get next task for an agent.
        
        Args:
            agent: Agent name
            
        Returns:
            Task data or None if no tasks available
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/tasks/next",
                json={"agent": agent}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("task"):
                logger.info(f"📋 Retrieved task: {data['task']['id']}")
                return data["task"]
            else:
                logger.info("No tasks available")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get next task: {e}")
            return None
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task data or None if not found
        """
        try:
            response = await self.client.get(f"{self.base_url}/tasks/{task_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("task")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Task {task_id} not found")
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task identifier
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/tasks/{task_id}/status",
                json={"status": status}
            )
            response.raise_for_status()
            logger.info(f"✅ Updated task {task_id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update task {task_id} status: {e}")
            return False
    
    async def log_event(self, agent: str, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Log an event to CoreHub.
        
        Args:
            agent: Agent name
            event_type: Type of event
            payload: Event payload data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/events/log",
                json={
                    "agent": agent,
                    "type": event_type,
                    "payload": payload
                }
            )
            response.raise_for_status()
            logger.debug(f"📝 Logged event: {event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to log event {event_type}: {e}")
            return False
    
    async def get_daily_report(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get daily report.
        
        Args:
            date: Report date (YYYY-MM-DD) or None for today
            
        Returns:
            Report data or None if failed
        """
        try:
            url = f"{self.base_url}/report/daily"
            if date:
                url += f"?report_date={date}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get daily report: {e}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check CoreHub health.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            return data.get("status") == "ok"
        except Exception as e:
            logger.error(f"CoreHub health check failed: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
