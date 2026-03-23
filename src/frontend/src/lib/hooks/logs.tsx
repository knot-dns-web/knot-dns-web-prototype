import { useCallback, useEffect, useState } from "react";
import { fetchLogs, type LogEntry } from "../api/logs";

export function useLogs(autoLoad = true) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);

    fetchLogs()
      .then((data) => setLogs(data))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!autoLoad) return;
    const id = window.setTimeout(() => reload(), 0);
    return () => window.clearTimeout(id);
  }, [autoLoad, reload]);

  return { logs, loading, error, reload };
}

