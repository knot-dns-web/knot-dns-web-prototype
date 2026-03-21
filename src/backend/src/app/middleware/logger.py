from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from ..logger.service import LoggerService
from ..auth.core import decode_access_token
import jwt

logger = LoggerService()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Логируем входящий запрос
        auth_header = request.headers.get("Authorization")
        user_str = "[user: anonymous]"
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_access_token(token)
                if payload:
                    user_str = f"[user: {payload.get('sub', 'unknown')}]"
            except jwt.PyJWTError:
                pass
        
        logger.write_log(
            f"{user_str} {request.method} {request.url.path}",
            level="INFO"
        )

        try:
            response = await call_next(request)
            
            # Логируем исходящий запрос
            logger.write_log(
                f"{user_str} {request.method} {request.url.path} -> {response.status_code}",
                level="INFO"
            )
            return response
            
        except Exception as e:
            logger.write_log(
                f"{user_str} {request.method} {request.url.path} ERROR: {str(e)}",
                level="ERROR"
            )
            raise