import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Request
import redis
import logging
from functools import wraps
import re

logger = logging.getLogger(__name__)


class SecurityService:
    """Comprehensive security service"""
    
    def __init__(self, secret_key: str, redis_client: redis.Redis):
        self.secret_key = secret_key
        self.redis_client = redis_client
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Rate limiting configuration
        self.rate_limits = {
            'api': {'requests': 100, 'window': 60},  # 100 requests per minute
            'inference': {'requests': 10, 'window': 60},  # 10 inferences per minute
            'upload': {'requests': 5, 'window': 60},  # 5 uploads per minute
            'websocket': {'connections': 10, 'window': 60}  # 10 connections per minute
        }
        
        # Input validation patterns
        self.validation_patterns = {
            'model_id': r'^[a-zA-Z0-9_-]+$',
            'file_name': r'^[a-zA-Z0-9._-]+$',
            'simulation_id': r'^[a-zA-Z0-9_-]+$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def check_rate_limit(self, identifier: str, limit_type: str) -> bool:
        """Check if request is within rate limit"""
        try:
            limit_config = self.rate_limits.get(limit_type)
            if not limit_config:
                return True
            
            key = f"rate_limit:{limit_type}:{identifier}"
            current_time = int(time.time())
            window_start = current_time - limit_config['window']
            
            # Get current count
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, limit_config['window'])
            results = pipe.execute()
            
            current_count = results[1]
            return current_count < limit_config['requests']
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    def validate_input(self, value: str, input_type: str) -> bool:
        """Validate input against patterns"""
        pattern = self.validation_patterns.get(input_type)
        if not pattern:
            return True
        
        return bool(re.match(pattern, value))
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    
    def validate_file_upload(self, file, max_size: int, allowed_types: List[str]) -> Dict[str, Any]:
        """Validate file upload"""
        try:
            # Check file size
            file_size = len(file.read())
            file.seek(0)  # Reset file pointer
            
            if file_size > max_size:
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
            
            # Sanitize filename
            safe_filename = self.sanitize_filename(file.filename)
            
            return {
                'valid': True,
                'file_size': file_size,
                'content_type': file.content_type,
                'safe_filename': safe_filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating file upload: {e}")
            raise HTTPException(status_code=400, detail="Invalid file upload")
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, session_token: str) -> bool:
        """Verify CSRF token"""
        return hmac.compare_digest(token, session_token)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "info"):
        """Log security event"""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'severity': severity,
                'details': details
            }
            
            # Store in Redis for analysis
            self.redis_client.lpush('security_events', str(event))
            
            # Keep only last 1000 events
            self.redis_client.ltrim('security_events', 0, 999)
            
            logger.info(f"Security event: {event_type} - {details}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def detect_anomalies(self, request: Request) -> bool:
        """Detect suspicious request patterns"""
        try:
            # Check for SQL injection patterns
            sql_patterns = [
                r'union\s+select', r'drop\s+table', r'delete\s+from',
                r'insert\s+into', r'update\s+set', r'exec\s*\('
            ]
            
            query_string = str(request.query_params)
            for pattern in sql_patterns:
                if re.search(pattern, query_string, re.IGNORECASE):
                    self.log_security_event('sql_injection_attempt', {
                        'pattern': pattern,
                        'query': query_string
                    }, 'high')
                    return True
            
            # Check for XSS patterns
            xss_patterns = [
                r'<script', r'javascript:', r'onload=', r'onerror=',
                r'<iframe', r'<object', r'<embed'
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, query_string, re.IGNORECASE):
                    self.log_security_event('xss_attempt', {
                        'pattern': pattern,
                        'query': query_string
                    }, 'high')
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return False
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        # Simple encryption for demo - use proper encryption in production
        return hashlib.sha256((data + self.secret_key).encode()).hexdigest()
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data"""
        anonymized = data.copy()
        
        # Remove or hash sensitive fields
        sensitive_fields = ['email', 'phone', 'ssn', 'credit_card']
        for field in sensitive_fields:
            if field in anonymized:
                anonymized[field] = self.encrypt_sensitive_data(str(anonymized[field]))
        
        return anonymized


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # Extract token from request
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        token = token[7:]  # Remove 'Bearer ' prefix
        
        # Verify token
        try:
            payload = jwt.decode(token, security_service.secret_key, algorithms=["HS256"])
            kwargs['user'] = payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return await f(*args, **kwargs)
    return decorated_function


def rate_limit(limit_type: str):
    """Decorator to apply rate limiting"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                return await f(*args, **kwargs)
            
            # Get client identifier
            client_ip = request.client.host
            identifier = f"{client_ip}:{request.url.path}"
            
            # Check rate limit
            if not security_service.check_rate_limit(identifier, limit_type):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            return await f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_input(input_type: str):
    """Decorator to validate input"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            # Validate inputs based on type
            if input_type == 'model_id' and 'model_id' in kwargs:
                if not security_service.validate_input(kwargs['model_id'], 'model_id'):
                    raise HTTPException(status_code=400, detail="Invalid model ID format")
            
            return await f(*args, **kwargs)
        return decorated_function
    return decorator


# Global security service instance
security_service = None  # Will be initialized in main.py
