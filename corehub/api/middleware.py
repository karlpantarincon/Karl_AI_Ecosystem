"""
Middleware configuration for CoreHub API.

Provides CORS, security headers, and request validation middleware.
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from corehub.api.schemas import ErrorResponse


class SecurityHeadersMiddleware:
    """Middleware to add security headers to responses."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                
                # Add security headers
                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"geolocation=(), microphone=(), camera=()"),
                ]
                
                # Add CORS headers for preflight requests
                cors_headers = [
                    (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
                    (b"access-control-allow-headers", b"Content-Type, Authorization"),
                    (b"access-control-max-age", b"86400"),
                ]
                
                headers.extend(security_headers)
                headers.extend(cors_headers)
                
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class RequestLoggingMiddleware:
    """Middleware to log HTTP requests."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                
                # Log request details
                method = scope.get("method", "UNKNOWN")
                path = scope.get("path", "UNKNOWN")
                status_code = message.get("status", 0)
                
                logger.info(
                    f"HTTP {method} {path} - {status_code} - "
                    f"{process_time:.3f}s"
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class RateLimitMiddleware:
    """Simple rate limiting middleware."""
    
    def __init__(self, app: FastAPI, requests_per_minute: int = 100):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # In production, use Redis or similar
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Get client IP (simplified)
        client_ip = scope.get("client", ["unknown"])[0]
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: timestamps for ip, timestamps in self.requests.items()
            if any(ts > current_time - 60 for ts in timestamps)
        }
        
        # Check rate limit
        if client_ip in self.requests:
            recent_requests = [
                ts for ts in self.requests[client_ip]
                if ts > current_time - 60
            ]
            
            if len(recent_requests) >= self.requests_per_minute:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": "Rate limit exceeded",
                        "details": {"limit": self.requests_per_minute, "window": "1 minute"}
                    }
                )
                await response(scope, receive, send)
                return
            
            self.requests[client_ip] = recent_requests + [current_time]
        else:
            self.requests[client_ip] = [current_time]
        
        await self.app(scope, receive, send)


class ErrorHandlingMiddleware:
    """Middleware to handle and format errors."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        except HTTPException as e:
            # Handle HTTP exceptions
            error_response = ErrorResponse(
                error=e.detail,
                details={"status_code": e.status_code}
            )
            response = JSONResponse(
                status_code=e.status_code,
                content=error_response.dict()
            )
            await response(scope, receive, send)
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {e}")
            error_response = ErrorResponse(
                error="Internal server error",
                details={"type": type(e).__name__}
            )
            response = JSONResponse(
                status_code=500,
                content=error_response.dict()
            )
            await response(scope, receive, send)


class RequestValidationMiddleware:
    """Middleware to validate request content."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Validate request size
        content_length = None
        headers = dict(scope.get("headers", []))
        
        if b"content-length" in headers:
            try:
                content_length = int(headers[b"content-length"])
                if content_length > 10 * 1024 * 1024:  # 10MB limit
                    response = JSONResponse(
                        status_code=413,
                        content={
                            "success": False,
                            "error": "Request too large",
                            "details": {"max_size": "10MB"}
                        }
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass
        
        await self.app(scope, receive, send)


def setup_cors(app: FastAPI):
    """Setup CORS middleware for v0.dev integration."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # v0.dev development
            "http://localhost:3001",  # Alternative dev port
            "https://v0.dev",         # v0.dev production
            "https://*.vercel.app",   # Vercel deployments
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page",
        ]
    )


def setup_security(app: FastAPI):
    """Setup security middleware."""
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "v0.dev"]
    )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)


def setup_logging(app: FastAPI):
    """Setup request logging middleware."""
    app.add_middleware(RequestLoggingMiddleware)


def setup_rate_limiting(app: FastAPI):
    """Setup rate limiting middleware."""
    app.add_middleware(RateLimitMiddleware, requests_per_minute=1000)


def setup_error_handling(app: FastAPI):
    """Setup error handling middleware."""
    app.add_middleware(ErrorHandlingMiddleware)


def setup_request_validation(app: FastAPI):
    """Setup request validation middleware."""
    app.add_middleware(RequestValidationMiddleware)


def setup_all_middleware(app: FastAPI):
    """Setup all middleware for production-ready API."""
    # Order matters - middleware is applied in reverse order
    
    # 1. Request validation (outermost)
    setup_request_validation(app)
    
    # 2. Error handling
    setup_error_handling(app)
    
    # 3. Rate limiting
    setup_rate_limiting(app)
    
    # 4. Request logging
    setup_logging(app)
    
    # 5. Security headers
    setup_security(app)
    
    # 6. CORS (innermost)
    setup_cors(app)


# Custom exception handlers will be added in main.py


# Request context middleware for additional data
class RequestContextMiddleware:
    """Middleware to add request context data."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Add request context
        scope["request_start_time"] = time.time()
        scope["request_id"] = str(time.time()).replace(".", "")
        
        await self.app(scope, receive, send)


def setup_request_context(app: FastAPI):
    """Setup request context middleware."""
    app.add_middleware(RequestContextMiddleware)


# Health check endpoints will be added in main.py
