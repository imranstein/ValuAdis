"""
Sentry Error Tracking Configuration

Configures Sentry for error tracking and performance monitoring
in production environment.
"""

import os
import logging
from typing import Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration
except ImportError:
    sentry_sdk = None
    FastApiIntegration = None
    SqlalchemyIntegration = None
    RedisIntegration = None
    LoggingIntegration = None
    StarletteIntegration = None

SENTRY_SDK_AVAILABLE = sentry_sdk is not None

from app.core.config import settings


class SentryManager:
    """Manages Sentry configuration and functionality"""
    
    def __init__(self):
        self.enabled = False
        self.dsn = settings.SENTRY_DSN
        self.environment = settings.ENVIRONMENT
        
    def initialize(self) -> bool:
        """Initialize Sentry SDK"""
        if not SENTRY_SDK_AVAILABLE or sentry_sdk is None:
            logging.info("Sentry SDK not installed; monitoring disabled")
            return False

        if not self.dsn or self.environment == "development":
            logging.info("Sentry disabled in development environment")
            return False
        
        try:
            # Configure Sentry integrations
            integrations = [
                FastApiIntegration(
                    auto_enabling_integrations=False,
                    transaction_style="endpoint"
                ),
                StarletteIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                # Custom logging integration
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ]
            
            # Initialize Sentry SDK
            sentry_sdk.init(
                dsn=self.dsn,
                integrations=integrations,
                environment=self.environment,
                traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                profiles_sample_rate=0.1,  # 10% of transactions for profiling
                
                # Release information
                release=os.getenv("APP_VERSION", "1.0.0"),
                
                # Before send callback for filtering
                before_send=self._before_send,
                
                # Ignore specific errors
                ignore_errors=[
                    "404 Not Found",
                    "403 Forbidden",
                    "401 Unauthorized"
                ],
                
                # Custom tags
                tags={
                    "service": "valuadis-backend",
                    "version": os.getenv("APP_VERSION", "1.0.0"),
                    "region": os.getenv("REGION", "ethiopia")
                }
            )
            
            self.enabled = True
            logging.info(f"Sentry initialized for environment: {self.environment}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {e}")
            return False
    
    def _before_send(self, event, hint):
        """Filter events before sending to Sentry"""
        # Filter out sensitive data
        if "request" in event and "data" in event["request"]:
            # Remove sensitive request data
            sensitive_keys = ["password", "token", "secret", "key"]
            for key in sensitive_keys:
                if key in event["request"]["data"]:
                    event["request"]["data"][key] = "[FILTERED]"
        
        # Filter out certain URLs
        if "request" in event and "url" in event["request"]:
            url = event["request"]["url"]
            if any(path in url for path in ["/health", "/metrics", "/favicon.ico"]):
                return None
        
        # Add custom context
        if "exception" in event:
            exception = event["exception"]["values"][0]
            if "type" in exception:
                event["tags"] = event.get("tags", {})
                event["tags"]["exception_type"] = exception["type"]
        
        return event
    
    def capture_exception(self, exception, extra_data=None):
        """Capture an exception with optional extra data"""
        if not self.enabled:
            return
        
        with sentry_sdk.configure_scope() as scope:
            if extra_data:
                for key, value in extra_data.items():
                    scope.set_extra(key, value)
            
            sentry_sdk.capture_exception(exception)
    
    def capture_message(self, message, level="info", extra_data=None):
        """Capture a message with optional extra data"""
        if not self.enabled:
            return
        
        with sentry_sdk.configure_scope() as scope:
            if extra_data:
                for key, value in extra_data.items():
                    scope.set_extra(key, value)
            
            sentry_sdk.capture_message(message, level=level)
    
    def set_user_context(self, user):
        """Set user context for all events"""
        if not self.enabled:
            return
        
        with sentry_sdk.configure_scope() as scope:
            scope.set_user({
                "id": str(user.id),
                "email": user.email,
                "username": user.full_name
            })
    
    def set_tag(self, key, value):
        """Set a custom tag"""
        if not self.enabled:
            return
        
        sentry_sdk.set_tag(key, value)
    
    def add_breadcrumb(self, category, message, level="info", data=None):
        """Add a breadcrumb for debugging"""
        if not self.enabled:
            return
        
        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            level=level,
            data=data or {}
        )
    
    def start_transaction(self, name, op="http.server"):
        """Start a performance monitoring transaction"""
        if not self.enabled:
            return None
        
        transaction = sentry_sdk.start_transaction(
            {"name": name, "op": op}
        )
        return transaction
    
    def finish_transaction(self, transaction, status="ok"):
        """Finish a transaction"""
        if not self.enabled or not transaction:
            return
        
        transaction.set_status(status)
        transaction.finish()


# Global Sentry manager instance
sentry_manager = SentryManager()


def init_sentry() -> bool:
    """Initialize Sentry for the application"""
    return sentry_manager.initialize()


def get_sentry_manager() -> SentryManager:
    """Get the global Sentry manager instance"""
    return sentry_manager


# Decorator for automatic exception capture
def sentry_capture_exception(extra_data=None):
    """Decorator to automatically capture exceptions to Sentry"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sentry_manager.capture_exception(e, extra_data)
                raise
        return wrapper
    return decorator


# Context manager for transactions
class SentryTransaction:
    """Context manager for Sentry transactions"""
    
    def __init__(self, name, op="http.server"):
        self.name = name
        self.op = op
        self.transaction = None
    
    def __enter__(self):
        self.transaction = sentry_manager.start_transaction(self.name, self.op)
        return self.transaction
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            status = "ok" if exc_type is None else "internal_error"
            sentry_manager.finish_transaction(self.transaction, status)


# Utility functions
def log_error_with_sentry(message, exception=None, extra_data=None):
    """Log error and send to Sentry"""
    logging.error(message, exc_info=exception)
    
    if exception:
        sentry_manager.capture_exception(exception, extra_data)
    else:
        sentry_manager.capture_message(message, level="error", extra_data=extra_data)


def log_warning_with_sentry(message, extra_data=None):
    """Log warning and send to Sentry"""
    logging.warning(message)
    sentry_manager.capture_message(message, level="warning", extra_data=extra_data)


def set_request_context(request, user=None):
    """Set request context for Sentry"""
    if not sentry_manager.enabled:
        return
    
    with sentry_sdk.configure_scope() as scope:
        # Set request context
        scope.set_context("request", {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            }
        })
        
        # Set user context if provided
        if user:
            scope.set_user({
                "id": str(user.id),
                "email": user.email,
                "username": user.full_name
            })
