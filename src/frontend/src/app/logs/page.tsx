"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useLogs } from "@/lib/hooks/logs";
import { HistoryTable } from "@/components/history/HistoryTable";
import { useAuth } from "@/lib/auth/context";

export default function LogsPage() {
  const router = useRouter();
  const { isReady, isAuthenticated } = useAuth();
  const { logs, loading, error, reload } = useLogs(true);

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
          <button
            type="button"
            onClick={() => reload()}
            className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-slate-200 hover:bg-white/[0.06]"
          >
            Обновить
          </button>
        </div>

        {loading && (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="h-12 rounded-lg bg-white/5 animate-pulse"
              />
            ))}
          </div>
        )}

        {!loading && error && <div className="text-red-400">{error}</div>}

        {!loading && !error && (
          <div className="rounded-lg border border-white/10 bg-white/[0.02] p-4">
            <HistoryTable logs={logs} />
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}

