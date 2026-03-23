"use client";

import { useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useLogs } from "@/lib/hooks/logs";
import { HistoryTable } from "@/components/history/HistoryTable";
import { useAuth } from "@/lib/auth/context";
import { LogEntry } from "@/lib/api/logs";

export default function LogsPage() {
  const router = useRouter();
  const { isReady, isAuthenticated } = useAuth();
  const { logs, loading, error } = useLogs(true);

  const filteredLogs = useMemo(() => {
    return logs.filter((log: LogEntry) => {
      const msg = (log.message ?? "").toLowerCase();

      const isZoneOrRecord = msg.includes("/zones") || msg.includes("/records");
      const isChangeMethod = /(post|put|delete)\s+\/(zones|records)/i.test(msg);
      const isSuccess = /->\s*2\d\d/.test(msg);

      return isZoneOrRecord && isChangeMethod && isSuccess;
    });
  }, [logs]);

  useEffect(() => {
    if (!isReady) return;
    if (!isAuthenticated) router.replace("/auth");
  }, [isReady, isAuthenticated, router]);

  return (
    <div className="page min-h-screen bg-slate-950 text-slate-100">
      <Header />
      <div className="px-8 md:px-16 py-16">
        <div className="flex items-center justify-between gap-4 mb-6">
          <h1 className="text-[30px] font-bold">История изменений</h1>
        </div>

        {loading && (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-12 rounded-lg bg-white/5 animate-pulse"
              />
            ))}
          </div>
        )}

        {!loading && error && <div className="text-red-400">{error}</div>}

        {!loading && !error && (
          <div className="rounded-lg bg-white/2 p-4">
            <HistoryTable logs={filteredLogs} />
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}

