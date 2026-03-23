import { apiFetch } from "@/lib/api/client";

export type LogEntry = {
  timestamp: string;
  level: string;
  message: string;
};

export async function fetchLogs(): Promise<LogEntry[]> {
  const res = await apiFetch("/api/logs");

  if (!res.ok) {
    const d = await res.json().catch(() => ({}));
    throw new Error(d.detail || "Ошибка загрузки истории изменений");
  }

  const data = await res.json().catch(() => ({}));
  return (data.logs ?? []) as LogEntry[];
}

