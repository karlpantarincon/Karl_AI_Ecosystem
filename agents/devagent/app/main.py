"""
DevAgent CLI - Main entry point.

This module provides the command-line interface for the DevAgent.
"""

import argparse
import asyncio
import sys
from typing import Optional

from loguru import logger

from agents.devagent.app.executor import DevAgentExecutor
from agents.devagent.tools.corehub_client import CoreHubClient


def setup_logging() -> None:
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )


async def run_once() -> None:
    """Run DevAgent once to process a single task."""
    logger.info("🚀 Starting DevAgent run_once...")
    
    try:
        # Initialize CoreHub client
        client = CoreHubClient()
        
        # Check if system is paused
        if await client.is_system_paused():
            logger.warning("⚠️ System is paused. Exiting.")
            return
        
        # Initialize executor
        executor = DevAgentExecutor(client)
        
        # Execute one task
        result = await executor.execute_task()
        
        if result:
            logger.success(f"✅ Task completed: {result}")
        else:
            logger.info("ℹ️ No tasks available")
            
    except Exception as e:
        logger.error(f"❌ DevAgent run_once failed: {e}")
        raise


async def run_loop(interval: int = 300) -> None:
    """
    Run DevAgent in continuous loop with advanced error handling and circuit breaker.
    
    Args:
        interval: Seconds between task checks
    """
    logger.info(f"🔄 Starting DevAgent loop with {interval}s interval...")
    
    # Circuit breaker state
    consecutive_failures = 0
    max_failures = 5
    circuit_open = False
    circuit_reset_time = 300  # 5 minutes
    
    # Performance metrics
    tasks_completed = 0
    errors_count = 0
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Initialize CoreHub client
        client = CoreHubClient()
        
        # Initialize executor
        executor = DevAgentExecutor(client)
        
        while True:
            try:
                # Circuit breaker check
                if circuit_open:
                    logger.warning("🔴 Circuit breaker is OPEN. Waiting for reset...")
                    await asyncio.sleep(circuit_reset_time)
                    circuit_open = False
                    consecutive_failures = 0
                    logger.info("🟢 Circuit breaker reset. Resuming operations...")
                    continue
                
                # Check if system is paused
                if await client.is_system_paused():
                    logger.warning("⚠️ System is paused. Waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute before checking again
                    continue
                
                # Execute one task
                result = await executor.execute_task()
                
                if result:
                    logger.success(f"✅ Task completed: {result}")
                    tasks_completed += 1
                    consecutive_failures = 0  # Reset failure counter on success
                else:
                    logger.info("ℹ️ No tasks available")
                
                # Log performance metrics every 10 tasks
                if tasks_completed % 10 == 0 and tasks_completed > 0:
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    tasks_per_hour = (tasks_completed / elapsed_time) * 3600
                    logger.info(f"📊 Performance: {tasks_completed} tasks completed, {tasks_per_hour:.1f} tasks/hour")
                
                # Wait before next iteration
                logger.info(f"⏳ Waiting {interval}s before next check...")
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal. Stopping...")
                break
            except Exception as e:
                errors_count += 1
                consecutive_failures += 1
                logger.error(f"❌ Error in loop iteration: {e}")
                
                # Check if circuit breaker should open
                if consecutive_failures >= max_failures:
                    circuit_open = True
                    logger.error(f"🔴 Circuit breaker OPENED after {consecutive_failures} consecutive failures")
                    continue
                
                # Exponential backoff for retries
                backoff_time = min(60 * (2 ** min(consecutive_failures - 1, 5)), 300)  # Max 5 minutes
                logger.info(f"⏳ Waiting {backoff_time}s before retry...")
                await asyncio.sleep(backoff_time)
                
    except Exception as e:
        logger.error(f"❌ DevAgent loop failed: {e}")
        raise


async def run_specific_task(task_id: str) -> None:
    """
    Run DevAgent for a specific task.
    
    Args:
        task_id: Task identifier to execute
    """
    logger.info(f"🎯 Starting DevAgent for specific task: {task_id}")
    
    try:
        # Initialize CoreHub client
        client = CoreHubClient()
        
        # Check if system is paused
        if await client.is_system_paused():
            logger.warning("⚠️ System is paused. Exiting.")
            return
        
        # Initialize executor
        executor = DevAgentExecutor(client)
        
        # Execute specific task
        result = await executor.execute_specific_task(task_id)
        
        if result:
            logger.success(f"✅ Task {task_id} completed: {result}")
        else:
            logger.warning(f"⚠️ Task {task_id} not found or not executable")
            
    except Exception as e:
        logger.error(f"❌ DevAgent specific task failed: {e}")
        raise


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DevAgent - AI Developer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agents.devagent.app.main run_once
  python -m agents.devagent.app.main loop --interval 300
  python -m agents.devagent.app.main run --task-id T-101
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run_once command
    run_once_parser = subparsers.add_parser("run_once", help="Execute one task")
    
    # loop command
    loop_parser = subparsers.add_parser("loop", help="Run in continuous loop")
    loop_parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Seconds between task checks (default: 300)"
    )
    loop_parser.add_argument(
        "--max-tasks",
        type=int,
        default=100,
        help="Maximum tasks per hour (default: 100)"
    )
    loop_parser.add_argument(
        "--priority",
        type=int,
        default=1,
        help="Task priority filter 1=highest, 5=lowest (default: 1)"
    )
    
    # run command
    run_parser = subparsers.add_parser("run", help="Execute specific task")
    run_parser.add_argument(
        "--task-id",
        required=True,
        help="Task identifier to execute"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging()
    
    # Execute command
    try:
        if args.command == "run_once":
            asyncio.run(run_once())
        elif args.command == "loop":
            asyncio.run(run_loop(args.interval))
        elif args.command == "run":
            asyncio.run(run_specific_task(args.task_id))
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
