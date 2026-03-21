from datetime import datetime

_logs = []

class LoggerService:

    def write_log(self, message: str, level: str = "INFO"):
        _logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        })

    def read_logs(self):
        return _logs