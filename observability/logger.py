"""
Observability module for logging and tracing agent activities.

This module provides structured logging capabilities to track:
- Agent execution flows
- Tool calls and responses
- A2A communication
- Memory access
- Errors and warnings
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from enum import Enum

from config.settings import get_settings

settings = get_settings()


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AgentLogger:
    """
    Structured logger for agent activities with support for
    real-time dashboard updates and file logging.
    """
    
    def __init__(self, name: str = "GitHubAgents"):
        """
        Initialize the agent logger.
        
        Args:
            name: Logger name
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Create logs directory if it doesn't exist
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler for persistent logs
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def _log_structured(
        self, 
        level: LogLevel, 
        message: str, 
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create structured log entry.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional structured data
            
        Returns:
            Dict containing the structured log entry
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "logger": self.name,
            "message": message,
            **kwargs
        }
        
        # Log to file/console
        log_method = getattr(self.logger, level.value.lower())
        log_method(f"{message} | {json.dumps(kwargs)}")
        
        return log_entry
    
    def agent_started(
        self, 
        agent_name: str, 
        agent_type: str, 
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Log agent start event.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent (Sequential, Parallel, Loop, etc.)
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.INFO,
            f"Agent started: {agent_name}",
            event_type="agent_started",
            agent_name=agent_name,
            agent_type=agent_type,
            **kwargs
        )
    
    def agent_completed(
        self, 
        agent_name: str, 
        duration: float, 
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Log agent completion event.
        
        Args:
            agent_name: Name of the agent
            duration: Execution duration in seconds
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.INFO,
            f"Agent completed: {agent_name}",
            event_type="agent_completed",
            agent_name=agent_name,
            duration_seconds=duration,
            **kwargs
        )
    
    def tool_called(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log tool call event.
        
        Args:
            tool_name: Name of the tool being called
            parameters: Tool parameters
            agent_name: Name of the calling agent
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.INFO,
            f"Tool called: {tool_name}",
            event_type="tool_called",
            tool_name=tool_name,
            parameters=parameters,
            agent_name=agent_name
        )
    
    def tool_response(
        self, 
        tool_name: str, 
        status: str,
        duration: float,
        result: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Log tool response event.
        
        Args:
            tool_name: Name of the tool
            status: Response status (success/error)
            duration: Call duration in seconds
            result: Tool result (optional, may be large)
            
        Returns:
            Structured log entry
        """
        log_data = {
            "event_type": "tool_response",
            "tool_name": tool_name,
            "status": status,
            "duration_seconds": duration
        }
        
        if result is not None and len(str(result)) < 500:
            log_data["result"] = result
        
        return self._log_structured(
            LogLevel.INFO,
            f"Tool response: {tool_name} ({status})",
            **log_data
        )
    
    def a2a_request(
        self, 
        source_service: str, 
        target_service: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log A2A protocol request.
        
        Args:
            source_service: Source service name
            target_service: Target service name
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.INFO,
            f"A2A Request: {source_service} → {target_service}",
            event_type="a2a_request",
            source_service=source_service,
            target_service=target_service,
            endpoint=endpoint,
            payload=payload
        )
    
    def a2a_response(
        self, 
        source_service: str, 
        target_service: str,
        status_code: int,
        duration: float
    ) -> Dict[str, Any]:
        """
        Log A2A protocol response.
        
        Args:
            source_service: Source service name
            target_service: Target service name
            status_code: HTTP status code
            duration: Request duration in seconds
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.INFO,
            f"A2A Response: {target_service} → {source_service} ({status_code})",
            event_type="a2a_response",
            source_service=source_service,
            target_service=target_service,
            status_code=status_code,
            duration_seconds=duration
        )
    
    def memory_access(
        self, 
        operation: str,
        key: str,
        service: str = "DatabaseSessionService",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Log memory access event.
        
        Args:
            operation: Operation type (read/write/search)
            key: Memory key accessed
            service: Memory service name
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.DEBUG,
            f"Memory {operation}: {key}",
            event_type="memory_access",
            operation=operation,
            key=key,
            service=service,
            **kwargs
        )
    
    def error(
        self, 
        message: str, 
        error: Optional[Exception] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Log error event.
        
        Args:
            message: Error message
            error: Exception object
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        error_data = {"event_type": "error", **kwargs}
        
        if error:
            error_data["error_type"] = type(error).__name__
            error_data["error_message"] = str(error)
        
        return self._log_structured(
            LogLevel.ERROR,
            message,
            **error_data
        )
    
    def warning(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Log warning event.
        
        Args:
            message: Warning message
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.WARNING,
            message,
            event_type="warning",
            **kwargs
        )
    
    def debug(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Log debug event.
        
        Args:
            message: Debug message
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.DEBUG,
            message,
            event_type="debug",
            **kwargs
        )
    
    def info(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Log info event.
        
        Args:
            message: Info message
            **kwargs: Additional context
            
        Returns:
            Structured log entry
        """
        return self._log_structured(
            LogLevel.INFO,
            message,
            event_type="info",
            **kwargs
        )


# Global logger instance
logger = AgentLogger("GitHubAgents")


def get_logger(name: Optional[str] = None) -> AgentLogger:
    """
    Get a logger instance.
    
    Args:
        name: Optional logger name
        
    Returns:
        AgentLogger instance
    """
    if name:
        return AgentLogger(name)
    return logger


if __name__ == "__main__":
    # Test logging
    test_logger = get_logger("TestAgent")
    
    test_logger.info("Testing logger setup")
    test_logger.agent_started("TestAgent", "Sequential", task="review-pr")
    test_logger.tool_called("get_pr_details", {"repo": "test", "pr": 1})
    test_logger.tool_response("get_pr_details", "success", 0.5)
    test_logger.agent_completed("TestAgent", 2.5)
    
    print("\n✅ Logger test complete! Check logs/agents.log for output.")

