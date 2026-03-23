from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from ..logger.service import LoggerService
from ..auth.core import decode_access_token
import jwt


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_session):
        super().__init__(app)
        self.get_session = get_session
    
    async def dispatch(self, request: Request, call_next):
        # Получаем пользователя
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
        
        # Получаем сессию БД
        async for session in self.get_session():
            try:
                logger_service = LoggerService(session)
                
                # Логируем входящий запрос
                await logger_service.write_log(
                    message=f"{user_str} {request.method} {request.url.path}",
                    level="INFO"
                )
                
                try:
                    response = await call_next(request)
                    
                    # Логируем исходящий ответ
                    await logger_service.write_log(
                        message=f"{user_str} {request.method} {request.url.path} -> {response.status_code}",
                        level="INFO"
                    )
                    
                    return response
                    
                except Exception as e:
                    # Логируем ошибку
                    await logger_service.write_log(
                        message=f"{user_str} {request.method} {request.url.path} ERROR: {str(e)}",
                        level="ERROR"
                    )
                    raise
                    
            finally:
                await session.close()