from datetime import datetime

_logs = []

class LoggerService:

    async def write_log(self, message: str, level: str = "INFO"):
        _logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        })

    async def read_logs(self):
        return _logs