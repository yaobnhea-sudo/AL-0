from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable
import redis

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, redis_client: redis.Redis, rate_limit: int = 100, window: int = 60):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = rate_limit
        self.window = window
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get client IP
        client_ip = request.client.host
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Check rate limit
        key = f"rate_limit:{client_ip}"
        current_time = int(time.time())
        window_start = current_time - self.window
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, self.window)
            results = pipe.execute()
            
            current_count = results[1]
            
            if current_count >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Allow request on Redis error
            pass
        
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security monitoring"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url.path} "
            f"in {process_time:.3f}s"
        )
        
        return response


class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor for suspicious activity"""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis_client = redis_client
        self.suspicious_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'exec\s*\(',
            r'<script',
            r'javascript:',
            r'onload=',
            r'onerror=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check for suspicious patterns
        query_string = str(request.query_params)
        
        for pattern in self.suspicious_patterns:
            if pattern in query_string.lower():
                logger.warning(
                    f"Suspicious activity detected from {request.client.host}: "
                    f"Pattern '{pattern}' in query string"
                )
                
                # Store security event
                try:
                    event = {
                        'timestamp': time.time(),
                        'ip': request.client.host,
                        'pattern': pattern,
                        'query': query_string,
                        'user_agent': request.headers.get('user-agent', ''),
                        'path': request.url.path
                    }
                    self.redis_client.lpush('security_events', str(event))
                except redis.RedisError as e:
                    logger.error(f"Error storing security event: {e}")
                
                # Return 400 for obvious attacks
                if any(sql_pattern in pattern for sql_pattern in ['union', 'drop', 'delete', 'insert', 'update']):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid request detected"
                    )
        
        return await call_next(request)


def setup_security_middleware(app: FastAPI, redis_client: redis.Redis):
    """Setup all security middleware"""
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add rate limiting
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
    
    # Add request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add security monitoring
    app.add_middleware(SecurityMonitoringMiddleware, redis_client=redis_client)
    
    # Add session middleware
    app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )
    
    # Add CORS middleware with security considerations
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Add GZIP compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)


def validate_file_upload(file, max_size: int, allowed_types: list) -> dict:
    """Validate file upload for security"""
    
    # Check file size
    if file.size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size} bytes"
        )
    
    # Check file type
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed types: {allowed_types}"
        )
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    if f'.{file_extension}' not in allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"File extension not allowed. Allowed extensions: {allowed_extensions}"
        )
    
    # Sanitize filename
    import re
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', file.filename)
    safe_filename = safe_filename[:255]  # Limit length
    
    return {
        'valid': True,
        'safe_filename': safe_filename,
        'file_size': file.size,
        'content_type': file.content_type
    }


def sanitize_input(input_string: str) -> str:
    """Sanitize user input"""
    import html
    import re
    
    # HTML escape
    sanitized = html.escape(input_string)
    
    # Remove potential SQL injection patterns
    sql_patterns = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'exec\s*\('
    ]
    
    for pattern in sql_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Remove potential XSS patterns
    xss_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>'
    ]
    
    for pattern in xss_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def generate_csrf_token() -> str:
    """Generate CSRF token"""
    import secrets
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token"""
    import hmac
    return hmac.compare_digest(token, session_token)


def log_security_event(event_type: str, details: dict, severity: str = "info"):
    """Log security event"""
    import json
    
    event = {
        'timestamp': time.time(),
        'event_type': event_type,
        'severity': severity,
        'details': details
    }
    
    logger.info(f"Security event: {event_type} - {details}")
    
    # Store in Redis for analysis
    try:
        redis_client = redis.Redis.from_url("redis://localhost:6379")
        redis_client.lpush('security_events', json.dumps(event))
        redis_client.ltrim('security_events', 0, 999)  # Keep last 1000 events
    except Exception as e:
        logger.error(f"Error storing security event: {e}")


def get_security_headers() -> dict:
    """Get security headers for responses"""
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
