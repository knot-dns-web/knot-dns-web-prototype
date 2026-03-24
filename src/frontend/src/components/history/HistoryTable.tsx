import type { LogEntry } from "@/lib/api/logs";

function formatTimestamp(ts: string) {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return d.toLocaleString("ru-RU");
}

export function HistoryTable({
  logs,
  emptyText = "Нет данных",
}: {
  logs: LogEntry[];
  emptyText?: string;
}) {
  return (
    <div className="overflow-x-auto">
      {logs.length === 0 ? (
        <p className="text-slate-400">{emptyText}</p>
      ) : (
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead>
            <tr className="border-b border-white/10 bg-white/[0.04] text-slate-400">
              <th className="px-4 py-3 font-medium">Время</th>
              <th className="px-4 py-3 font-medium">Уровень</th>
              <th className="px-4 py-3 font-medium">Сообщение</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l, idx) => (
              <tr
                key={`${l.timestamp}-${l.level}-${idx}`}
                className="border-b border-white/5 hover:bg-white/[0.03]"
              >
                <td className="px-4 py-3 whitespace-nowrap">
                  {formatTimestamp(l.timestamp)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">{l.level}</td>
                <td className="px-4 py-3 max-w-[520px] break-all">
                  {l.message}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

