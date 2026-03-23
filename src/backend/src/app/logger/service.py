from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import Optional, List
from .schema import Log, LogOut
import logging

logger = logging.getLogger(__name__)


class LoggerService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def write_log(self, message: str, level: str = "INFO"):
        try:
            log = Log(
                timestamp=datetime.now(),
                level=level,
                message=message
            )
            
            self.session.add(log)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
            await self.session.rollback()
    
    async def read_logs(self) -> List[LogOut]:
        try:
            stmt = select(Log).order_by(desc(Log.timestamp))
            result = await self.session.execute(stmt)
            logs = result.scalars().all()
            
            return [LogOut.model_validate(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
            return []
    
    async def clear_logs(self) -> bool:
        try:
            stmt = select(Log)
            result = await self.session.execute(stmt)
            logs = result.scalars().all()
            
            for log in logs:
                await self.session.delete(log)
            
            await self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            await self.session.rollback()
            return False