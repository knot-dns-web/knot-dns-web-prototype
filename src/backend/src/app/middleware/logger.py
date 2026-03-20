from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from ..logger.service import LoggerService

logger = LoggerService()


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # до запроса
        logger.write_log(
            f"{request.method} {request.url.path}",
            level="INFO"
        )

        try:
            response = await call_next(request)

            # после запроса
            logger.write_log(
                f"{request.method} {request.url.path} -> {response.status_code}",
                level="INFO"
            )

            return response

        except Exception as e:
            logger.write_log(
                f"{request.method} {request.url.path} ERROR: {str(e)}",
                level="ERROR"
            )
            raise